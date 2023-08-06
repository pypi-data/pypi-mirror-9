import logging

logger = logging.getLogger(__name__)

from nymms.schemas import Result, types
from nymms.daemon import NymmsDaemon
from nymms.resources import Monitor
from nymms.utils import commands
from nymms.config.yaml_config import load_config, EmptyConfig

import arrow


TIMEOUT_OUTPUT = "Command timed out after %d seconds."


class Probe(NymmsDaemon):
    state_manager = None

    def get_private_context(self, private_context_file):
        if not private_context_file:
            return None
        try:
            return load_config(private_context_file)[1]
        except (IOError, EmptyConfig):
            logger.exception("Unable to open private context file: %s",
                             private_context_file)
            return None

    # TODO: This calls on _state_manager but setting up of the _state_manager
    #       needs to be handled in the subclass.  Not sure how I should handle
    #       this, but I really like the idea of these being base class
    #       methods since in reality all reactors should have some sort of
    #       state backend, even if its a no-op
    def get_state(self, task_id):
        return self.state_manager.get_state(task_id)

    def get_task(self, **kwargs):
        raise NotImplementedError

    def resubmit_task(self, task, delay, **kwargs):
        raise NotImplementedError

    def submit_result(self, result, **kwargs):
        raise NotImplementedError

    def delete_task(self, task):
        raise NotImplementedError

    def execute_task(self, task, timeout, **kwargs):
        log_prefix = "%s - " % (task.id,)
        monitor = Monitor.registry[task.context['monitor']['name']]
        command = monitor.command.command_string
        current_attempt = int(task.attempt) + 1
        logger.debug(log_prefix + "attempt %d, executing: %s", current_attempt,
                     command)
        result = Result({'id': task.id,
                         'timestamp': task.created,
                         'task_context': task.context})
        try:
            output = monitor.execute(task.context, timeout,
                                     self._private_context)
            result.output = output
            result.state = types.STATE_OK
        except commands.CommandException as e:
            if isinstance(e, commands.CommandFailure):
                result.state = e.return_code
                result.output = e.output
            if isinstance(e, commands.CommandTimeout):
                result.state = types.STATE_UNKNOWN
                result.output = (TIMEOUT_OUTPUT % timeout)
        except Exception as e:
            result.state = types.STATE_UNKNOWN
            result.output = str(e)
        result.state_type = types.STATE_TYPE_HARD
        result.validate()
        return result

    def expire_task(self, task, task_expiration):
        if task_expiration:
            now = arrow.get()
            task_lifetime = now.timestamp - task.created.timestamp
            if task_lifetime > task_expiration:
                logger.debug("Task %s is older than expiration limit %d. "
                             "Skipping.", task.id, task_expiration)
                return True
            return False
        return False

    def handle_task(self, task, **kwargs):
        log_prefix = "%s - " % (task.id,)
        task_expiration = kwargs.get('task_expiration', None)
        if self.expire_task(task, task_expiration):
            return None
        # Used to add the command context to the task
        monitor = Monitor.registry[task.context['monitor']['name']]
        command = monitor.command
        task.context = command.build_context(task.context)
        previous_state = self.get_state(task.id)
        # check if the timeout is defined on the task first, if not then
        # go with what was passed into handle_task via run
        timeout = task.context.get('monitor_timeout',
                                   kwargs.get('monitor_timeout'))
        max_retries = task.context.get('max_retries',
                                       kwargs.get('max_retries'))
        last_attempt = int(task.attempt)
        current_attempt = last_attempt + 1
        result = self.execute_task(task, timeout, **kwargs)
        # Trying to emulate this:
        # http://nagios.sourceforge.net/docs/3_0/statetypes.html
        if result.state == types.STATE_OK:
            if (previous_state and not
                    previous_state.state == types.STATE_OK and
                    previous_state.state_type == types.STATE_TYPE_SOFT):
                result.state_type = types.STATE_TYPE_SOFT
        else:
            logger.debug(log_prefix + "current_attempt: %d, max_retries: %d",
                         current_attempt, max_retries)
            if current_attempt <= max_retries:
                # XXX Hate this logic - hope to find a cleaner way to handle
                #     it someday.
                if (not previous_state or
                   previous_state.state_type == types.STATE_TYPE_SOFT or
                   previous_state.state == types.STATE_OK):
                    result.state_type = types.STATE_TYPE_SOFT
                    delay = task.context.get('retry_delay',
                                             kwargs.get('retry_delay'))
                    delay = max(delay, 0)
                    logger.debug('Resubmitting task with %ds delay.', delay)
                    self.resubmit_task(task, delay, **kwargs)
            else:
                logger.debug("Retry limit hit, not resubmitting.")
        result.validate()
        return result

    def run(self, **kwargs):
        """ This will run in a tight loop. It is expected that the subclass's
        get_task() method will introduce a delay if the results queue is
        empty.
        """
        private_context_file = kwargs.get('private_context_file', None)
        self._private_context = self.get_private_context(private_context_file)
        while True:
            task = self.get_task(**kwargs)
            if not task:
                logger.debug("Task queue is empty.")
                continue
            result = self.handle_task(task, **kwargs)
            if result:
                self.submit_result(result, **kwargs)
            self.delete_task(task)
