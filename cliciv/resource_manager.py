from typing import List

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import ResourcesRegisterForUpdates, ResourcesNewState


class ResourceManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.resource_state = ResourceState()
        super(ResourceManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, ResourcesRegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, ResourcesNewState(self.resource_state))
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))


class ResourceState(object):
    def __init__(self):
        self.materials = {
            "food": 1.0,
            "water": 2.0,
            "wood": 2.6,
            "stone": 0.0,
        }
