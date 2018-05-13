from typing import List

from thespian.actors import Actor, ActorAddress

from cliciv.messages import ResourcesRegisterForUpdates, ResourcesMessage, ResourcesNewState


class ResourceManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.resource_state = ResourceState()

    def receiveMessage(self, msg: ResourcesMessage, sender: str):
        if isinstance(msg, ResourcesRegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, ResourcesNewState(self.resource_state))
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))


class ResourceState(object):
    def __init__(self):
        self.occupations = {
            "gatherer": 2,
            "idle": 3,
            "builder": 0,
            "woodcutter": 1,
        }
        self.resources = {
            "food": 1.0,
            "water": 2.0,
            "wood": 2.6,
            "stone": 0.0,
        }
