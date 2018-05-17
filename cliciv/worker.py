import logging
from typing import Dict

from thespian.actors import Actor, ActorExitRequest, WakeupMessage

from cliciv.messages import ResourcesRequest, Start, ResourcesRequestGranted, ResourcesRequestDenied, ResourcesProduced, \
    WorkerProfile
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager

logger = logging.getLogger(__name__)


class Profile(object):
    def __init__(self, needs=None, produces=None):
        self.needs = needs or {}
        self.produces = produces or {}


Profiles = {
    'gatherer': Profile(
        needs={},
        produces={
            'food': 0.5
        }
    ),
    'woodcutter': Profile(
        needs={
            'food': 1
        },
        produces={
            'wood': 1
        }
    ),
    'builder': Profile(),
}


class WorkerFactory():
    def __init__(self, worker_manager: Actor):
        self.worker_manager = worker_manager
        super(WorkerFactory, self).__init__()

    def from_config(self, config: Dict[str, int]):
        return {
            occupation: self.generate_n(occupation, num)
            for occupation, num in config.items()
        }

    def generate_n(self, occupation: str, num: int):
        return [
            self.of_type(occupation) for _ in range(num)
        ]

    def of_type(self, occupation: str):
        return self.worker_manager.createActor(Worker)


class Worker(Actor):
    def __init__(self):
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self._profile = None
        self._epoch = 0 # Track to ensure stale wakeups don't generate extra resources
        super(Worker, self).__init__()
    
    def receiveMessage(self, msg, sender):
        logger.debug("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, WorkerProfile):
            logger.debug("New profile: {}".format(msg.new_profile))
            self._profile = msg.new_profile
            self._epoch += 1
            self.wakeupAfter(1, self._epoch)
        elif isinstance(msg, Start) or (isinstance(msg, WakeupMessage) and msg.payload == self._epoch):
            self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
            self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
            self.start_work()
        elif isinstance(msg, ResourcesRequestGranted):
            self.produce_output()
            self.wakeupAfter(1, self._epoch)
        elif isinstance(msg, ResourcesRequestDenied):
            logger.warn("Worker {} request for resources denied".format(self))
            self.wakeupAfter(1, self._epoch)
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

    def start_work(self):
        if not self._profile:
            # ERROR LOG
            return

        self.send(self.resources_manager, ResourcesRequest(self._profile.needs))

    def produce_output(self):
        if not self._profile:
            # ERROR LOG
            return

        self.send(self.resources_manager, ResourcesProduced(self._profile.produces))
