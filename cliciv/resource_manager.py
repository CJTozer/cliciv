import logging
from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import ResourcesNewState, ResourcesRequest, ResourcesRequestGranted, ResourcesRequestDenied, \
    RegisterForUpdates, ResourcesProduced, InitialState

logger = logging.getLogger(__name__)


class ResourceManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.resource_state = None
        super(ResourceManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        logger.info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, InitialState):
            self.resource_state = ResourceState(msg.state['resources'])
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
    def __init__(self, initial_resources):
        self.resources = initial_resources

    def satisfy(self, requested: Dict[str, float]) -> bool:
        if not requested or all([
            self.resources.get(resource, 0.0) >= amount
            for resource, amount in requested.items()
        ]):
            for resource, amount in requested.items():
                self.resources[resource] -= amount
            return True
        return False

    def store(self, resources: Dict[str, float]):
        for resource, amount in resources.items():
            self.resources[resource] = self.resources.get(resource, 0.0) + amount
