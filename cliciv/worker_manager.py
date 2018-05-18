import logging
from typing import List, Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import WorkersNewState, TechnologyNewState, Start, RegisterForUpdates, WorkerChangeRequest, \
    WorkerProfile
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker import WorkerFactory, Profiles

logger = logging.getLogger(__name__)


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
        logger.info("{}/{}".format(msg, self))
        notify_change = False

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
        elif isinstance(msg, WorkerChangeRequest):
            new_gatherer_count = len(self.workers.get('gatherer', [])) - msg.increment
            new_type_count = len(self.workers.get(msg.worker_type, [])) + msg.increment
            if new_gatherer_count >= 0 and new_type_count >= 0:
                # The transition seems reasonable
                if msg.increment > 0:
                    # Move workers from gathering to a new job
                    for _ in range(msg.increment):
                        worker = self.workers['gatherer'].pop()
                        self._assign_worker(worker, msg.worker_type)
                else:
                    # Move workers back to gathering
                    for _ in range(-msg.increment):
                        worker = self.workers[msg.worker_type].pop()
                        self._assign_worker(worker, 'gatherer')

                notify_change = True

        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

        self.worker_state.recalculate(self.workers)

        if notify_change:
            for actor in self.registered:
                self.send(actor, WorkersNewState(self.worker_state))

    def workers_list(self):
        return [
            w
            for _, worker_list in self.workers.items()
            for w in worker_list
        ]

    def start_workers(self):
        for worker_type, worker_list in self.workers.items():
            for worker in worker_list:
                self.send(worker, WorkerProfile(Profiles[worker_type]))
                self.send(worker, Start())

    def stop_workers(self):
        for worker in self.workers_list():
            self.send(worker, ActorExitRequest())

    def _assign_worker(self, worker, worker_type):
        self.send(worker, WorkerProfile(Profiles[worker_type]))
        if worker_type not in self.workers:
            self.workers[worker_type] = []
        self.workers[worker_type].append(worker)


class WorkerState(object):
    def __init__(self):
        self.occupations = {
            "gatherer": 5,
            "builder": 0,
            "woodcutter": 0,
        }

    def recalculate(self, workers):
        self.occupations = {}
        for worker_type, workers in workers.items():
            self.occupations[worker_type] = len(workers)

