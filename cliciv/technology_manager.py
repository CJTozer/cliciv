import logging
from typing import List

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import RegisterForUpdates, TechnologyNewState, InitialState

logger = logging.getLogger(__name__)


class TechnologyManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.technology_state = None
        super(TechnologyManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        logger.info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, InitialState):
            self.technology_state = TechnologyState(msg.state['technology'])
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, TechnologyNewState(self.technology_state))
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))


class TechnologyState(object):
    def __init__(self, data):
        self.__dict__ = data
