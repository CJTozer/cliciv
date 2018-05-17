import logging
from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import ResourcesNewState, ResourcesRequest, ResourcesRequestGranted, ResourcesRequestDenied, \
    RegisterForUpdates, ResourcesProduced

logger = logging.getLogger(__name__)


class ResourceManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.resource_state = ResourceState()
        super(ResourceManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        logger.debug("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, ResourcesNewState(self.resource_state))
        elif isinstance(msg, ResourcesRequest):
            if self.resource_state.satisfy(msg.requested):
                self.send(sender, ResourcesRequestGranted())
                self.notify_all()
            else:
                self.send(sender, ResourcesRequestDenied())
        elif isinstance(msg, ResourcesProduced):
            self.resource_state.store(msg.produced)
            self.notify_all()
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

    def notify_all(self):
        for r in self.registered:
            self.send(r, ResourcesNewState(self.resource_state))


class ResourceState(object):
    def __init__(self):
        self.materials = {
            "food": 100.0,
            "water": 100.0,
            "wood": 100.0,
            "stone": 100.0,
        }

    def satisfy(self, requested: Dict[str, float]) -> bool:
        if not requested or all([
            self.materials.get(material, 0.0) >= amount
            for material, amount in requested.items()
        ]):
            for material, amount in requested.items():
                self.materials[material] -= amount
            return True
        return False

    def store(self, resources: Dict[str, float]):
        for material, amount in resources.items():
            self.materials[material] = self.materials.get(material, 0.0) + amount
