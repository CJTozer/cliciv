import logging
from typing import List, Dict

import re
from thespian.actors import Actor, ActorExitRequest

from cliciv.building_manager import BuildingManager
from cliciv.messages import WorkersNewState, TechnologyNewState, Start, RegisterForUpdates, WorkerChangeRequest, \
    WorkerProfile, InitialState, BuildTarget, BuilderAssignRequest, BuildersAssigned
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager, TechnologyState
from cliciv.utils.data import dict_from_data
from cliciv.worker import WorkerFactory, Profiles

logger = logging.getLogger(__name__)


class WorkerManager(Actor):
    def __init__(self):
        self.started = False
        self.registered = []
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self.technology_state: TechnologyState = None
        self.worker_state: WorkerState = None
        self.worker_factory = None
        self.workers: Dict[str, List[Actor]] = {}
        self.building_manager: Actor = None
        self.buildings = {}
        self.buildings_data = dict_from_data('buildings')
        super(WorkerManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        logger.info("{}/{}".format(msg, self))
        notify_change = False

        if isinstance(msg, ActorExitRequest):
            self.stop_workers()
        elif isinstance(msg, InitialState):
            self.worker_state = WorkerState(msg.state['workers'])
            if self.started:
                self.start()
        elif isinstance(msg, Start):
            # Can't guarantee the order of InitialState and Start, so cope with both orders
            if self.worker_state:
                self.start()
            else:
                logger.info("Waiting for initial state before starting")
                self.started = True
                return
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, WorkersNewState(self.worker_state))
        elif isinstance(msg, TechnologyNewState):
            self._handle_tech_update(msg.new_state)
            self.technology_state = msg.new_state
        elif isinstance(msg, WorkerChangeRequest):
            # Builders are not handled this way
            if msg.worker_type == 'builder':
                logger.debug("Ignoring message {} to change workers into builders".format(msg))
                return

            if self._transition_ok(msg, msg.worker_type):
                self._move_n_workers(msg.worker_type, msg.increment)
                notify_change = True
        elif isinstance(msg, BuilderAssignRequest):
            if self._transition_ok(msg, 'builder'):
                if self._builders_allowed(msg.building_id, msg.increment):
                    self._move_n_workers('builder', msg.increment)
                    self._assign_builders(msg.building_id, msg.increment)
                    notify_change = True
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

        self.worker_state.recalculate(self.workers)

        if notify_change:
            for actor in self.registered:
                self.send(actor, WorkersNewState(self.worker_state))

    def _move_n_workers(self, worker_type, increment):
        if increment > 0:
            from_type = 'gatherer'
            to_type = worker_type
        else:
            from_type = worker_type
            to_type = 'gatherer'

        for _ in range(abs(increment)):
            worker = self.workers[from_type].pop()
            self._assign_worker(worker, to_type)

    def _transition_ok(self, msg, worker_type):
        new_gatherer_count = len(self.workers.get('gatherer', [])) - msg.increment
        new_type_count = len(self.workers.get(worker_type, [])) + msg.increment
        transition_ok = new_gatherer_count >= 0 and new_type_count >= 0
        if not transition_ok:
            logger.info("Rejected transition: increment {} would result in {} gatherers and {} {}s".format(
                msg.increment, new_gatherer_count, new_type_count, worker_type
            ))
        return transition_ok

    def start(self):
        self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
        self.building_manager = self.createActor(BuildingManager, globalName="building_manager")
        self.worker_factory = WorkerFactory(self)
        self.workers = self.worker_factory.from_config(
            self.worker_state.occupations
        )

        # Register for tech updates
        self.send(self.technology_manager, RegisterForUpdates())

        # Start Workers
        self.start_workers()

    def workers_list(self):
        return [
            w
            for _, worker_list in self.workers.items()
            for w in worker_list
        ]

    def start_workers(self):
        logger.info(self.workers)
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

    def _handle_tech_update(self, new_state):
        for research_id, research_info in new_state.completed_research.items():
            logger.info("Newly completed research '{}': {}".format(research_id, new_state.completed_research))
            if 'profile-update' in research_info['produces']:
                updated_occupations = Profiles.update(research_id, research_info['produces']['profile-update'])
                # Refresh each affected worker's profile
                for occupation in updated_occupations:
                    for worker in self.workers[occupation]:
                        self.send(worker, WorkerProfile(Profiles[occupation]))

    def _assign_builders(self, building_id, increment):
        if increment == 0:
            # Already have the correct number of builders
            return

        if increment > 0:
            # More builders required
            idle_builders = [
                b for b in self.workers['builder']
                if not any([
                    b in active_builders
                    for _, active_builders in self.buildings.items()
                ])
            ]
            if len(idle_builders) < increment:
                # Cannot handle the request
                logger.warning("Cannot handle request for {} more builders, only {} idle.".format(
                    increment, len(idle_builders)))
                return
            if building_id not in self.buildings:
                self.buildings[building_id] = []
            for _ in range(increment):
                builder = idle_builders.pop()
                self.buildings[building_id].append(builder)
                self.send(builder, BuildTarget(building_id))

        else:
            # Fewer builders required
            if len(self.buildings.get(building_id, [])) < -increment:
                # Cannot handle the request
                logger.warning("Cannot handle request for {} fewer builders, only {} building.".format(
                    increment, len(self.buildings[building_id])))
                return
            for _ in range(-increment):
                builder = self.buildings[building_id].pop()
                self.send(builder, BuildTarget(None))

        # Something has changed, notify the building_manager.
        logger.info("self.buildings: {}".format(self.buildings))
        new_num = len(self.buildings[building_id])
        self.send(self.building_manager, BuildersAssigned(building_id, new_num))

    def _builders_allowed(self, building_id, increment):
        building_info = self._building_info_from_id(building_id)
        max_builders = building_info.get('max_builders', 1)
        current_builders = len(self.buildings.get(building_id, []))
        allowed = current_builders + increment <= max_builders
        if not allowed:
            logger.debug("Request for {} more builders on building {}, but max is {}".format(
                increment, building_id, max_builders
            ))
        return allowed

    def _building_info_from_id(self, building_id):
        building_type = re.sub('(.*?)\d*','\\1', building_id)
        return self.buildings_data[building_type]


class WorkerState(object):
    def __init__(self, initial_occupations):
        self.occupations = initial_occupations

    def recalculate(self, workers):
        self.occupations = {}
        for worker_type, workers in workers.items():
            self.occupations[worker_type] = len(workers)

