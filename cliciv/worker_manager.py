from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import WorkersNewState, TechnologyNewState, Start, RegisterForUpdates
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker import WorkerFactory


class WorkerManager(Actor):
    def __init__(self):
        self.registered = []
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self.technology_state = None
        self.worker_state = WorkerState()
        self.worker_factory = None
        self.workers: Dict[str, List[Actor]] = {}
        super(WorkerManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        # self.logger().info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            self.stop_workers()
        elif isinstance(msg, Start):
            self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
            self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
            self.worker_factory = WorkerFactory(self)
            self.workers = self.worker_factory.from_config(
                self.worker_state.occupations
            )
            # Register for tech updates
            self.send(self.technology_manager, RegisterForUpdates())
            # Start Workers
            self.start_workers()
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, WorkersNewState(self.worker_state))
        elif isinstance(msg, TechnologyNewState):
            self.technology_state = msg.new_state
        # else:
        #     self.logger().error("Ignoring unexpected message: {}".format(msg))

    def workers_list(self):
        return [
            w
            for _, worker_list in self.workers.items()
            for w in worker_list
        ]

    def start_workers(self):
        for worker in self.workers_list():
            self.send(worker, Start())

    def stop_workers(self):
        for worker in self.workers_list():
            self.send(worker, ActorExitRequest())


class WorkerState(object):
    def __init__(self):
        self.occupations = {
            "idle": 1,
            "gatherer": 3,
            "builder": 0,
            "woodcutter": 0,
        }
