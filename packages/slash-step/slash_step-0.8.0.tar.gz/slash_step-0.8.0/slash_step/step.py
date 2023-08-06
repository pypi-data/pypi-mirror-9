import logbook
from . import hooks

_LOGGER_NAME = "slash.step"
_STEP_LOG_LEVEL = logbook.NOTICE

_logger = logbook.Logger(_LOGGER_NAME)


class Step(object):

    def __init__(self, msg, *args, **kwargs):
        super(Step, self).__init__()
        self.message = msg.format(*args, **kwargs)

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<Step {0!r}>".format(self.message)

    def _start(self):
        _logger.log(_STEP_LOG_LEVEL, self.message)
        hooks.step_start.trigger({})

    def _success(self):
        hooks.step_success.trigger({})

    def _error(self):
        hooks.step_error.trigger({})

    def _end(self):
        hooks.step_end.trigger({})

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type is None:
                self._success()
            else:
                self._error()
        finally:
            self._end()
