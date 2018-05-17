import logging
from enum import Enum

from cliciv.messages import WorkerChangeRequest

logger = logging.getLogger(__name__)


class CommandHandler(object):

    def __init__(self, coordinator):
        self._coord = coordinator

    def increment(self, command_type, arg, amount):
        if command_type == CommandType.OCCUPATIONS:
            msg = WorkerChangeRequest(arg, amount)
            self._coord.actor_system.tell(
                self._coord.worker_manager,
                msg
            )


class CommandType(Enum):
    OCCUPATIONS = 1
