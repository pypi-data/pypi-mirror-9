from .__version__ import __version__
from . import hooks
from .step import Step, _LOGGER_NAME, _STEP_LOG_LEVEL
import slash.log

slash.log.set_log_color(_LOGGER_NAME, _STEP_LOG_LEVEL, "blue")

STEP = Step
