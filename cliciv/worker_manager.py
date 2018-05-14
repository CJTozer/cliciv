from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import WorkerManagerSetup, WorkersRegisterForUpdates, WorkersNewState, WorkersStart, WorkerStart, \
    WorkerSetup, TechnologyRegisterForUpdates, TechnologyNewState
from cliciv.worker import WorkerFactory


class WorkerManager(Actor):
    def __init__(self):
        self.registered = []
        self.resources_manager: str = None
        self.technology_manager: str = None
        self.technology_state = None
        self.worker_state = WorkerState()
        self.worker_factory = None
        self.workers: Dict[str, List[Actor]] = {}
        super(WorkerManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        self.logger().info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            self.stop_workers()
        elif isinstance(msg, WorkerManagerSetup):
            self.resources_manager = msg.resource_manager
            self.technology_manager = msg.technology_manager
            self.worker_factory = WorkerFactory(self)
            self.workers = self.worker_factory.from_config(
                self.worker_state.occupations
            )
            self.setup_workers()
            # Register for tech updates
            self.send(self.technology_manager, TechnologyRegisterForUpdates())
        elif isinstance(msg, WorkersStart):
            self.start_workers()
        elif isinstance(msg, WorkersRegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, WorkersNewState(self.worker_state))
        elif isinstance(msg, TechnologyNewState):
            self.technology_state = msg.new_state
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))

    def workers_list(self):
        return [
            w
            for _, worker_list in self.workers.items()
            for w in worker_list
        ]

    def setup_workers(self):
        for worker in self.workers_list():
            self.send(worker, WorkerSetup(
                self.resources_manager,
                self.technology_manager
            ))

    def start_workers(self):
        for worker in self.workers_list():
            self.send(worker, WorkerStart())

    def stop_workers(self):
        for worker in self.workers_list():
            self.send(worker, ActorExitRequest())


class WorkerState(object):
    def __init__(self):
        self.occupations = {
            "gatherer": 2,
            "idle": 3,
            "builder": 0,
            "woodcutter": 1,
        }
