from typing import List

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import RegisterForUpdates, TechnologyNewState


class TechnologyManager(Actor):
    def __init__(self):
        self.registered: List[str] = []
        self.technology_state = TechnologyState()
        super(TechnologyManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        # self.logger().info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, TechnologyNewState(self.technology_state))
        # else:
        #     self.logger().error("Ignoring unexpected message: {}".format(msg))


class TechnologyState(object):
    def __init__(self):
        self.unlocked_occupations = ["idle", "gatherer", "builder"]
        self.unlocked_materials = ["food", "wood"]
