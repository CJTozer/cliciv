from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import WorkerManagerSetup


class WorkerManager(Actor):
    def __init__(self):
        self.resources_manager: str = None
        self.technology_manager: str = None
        self.workers: Dict[str, List[Actor]] = {}
        super(WorkerManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        if isinstance(msg, ActorExitRequest):
            pass
        if isinstance(msg, WorkerManagerSetup):
            self.resources_manager = msg.resource_manager
            self.technology_manager = msg.technology_manager
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))


class WorkerState(object):
    def __init__(self):
        self.occupations = {
            "gatherer": 2,
            "idle": 3,
            "builder": 0,
            "woodcutter": 1,
        }
