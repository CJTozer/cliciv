import logging
from typing import List

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import RegisterForUpdates, TechnologyNewState, InitialState, TechnologyProduced
from cliciv.utils.data import dict_from_data

logger = logging.getLogger(__name__)


class TechnologyManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.technology_state = None
        self.tech_tree = dict_from_data('technology')
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
        elif isinstance(msg, TechnologyProduced):
            old_amount = self.technology_state.research_accrued.get(msg.area, 0)
            self.technology_state.research_accrued[msg.area] = old_amount + msg.amount
            self.check_for_unlocked_tech()
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

    def notify_all(self):
        for r in self.registered:
            self.send(r, TechnologyNewState(self.technology_state))

    def check_for_unlocked_tech(self):
        unlocked_research = {}
        for tech, tech_info in self.tech_tree.items():
            if self.technology_state.satisfies(tech_info['requires']):
                unlocked_research[tech] = tech_info
        if set(unlocked_research.keys()) != set(self.technology_state.unlocked_research.keys()):
            logger.info("New research unlocked: {}".format(
                [t for t in unlocked_research.keys() if t not in self.technology_state.unlocked_research]
            ))
            self.technology_state.unlocked_research = unlocked_research
            self.notify_all()


class TechnologyState(object):
    def __init__(self, data):
        self.__dict__ = data

    def satisfies(self, required):
        # Check whether enough tech has been accrued
        return all([
            self.research_accrued.get(k, 0) >= v
            for k, v in required['research_accrued'].items()
        ])
