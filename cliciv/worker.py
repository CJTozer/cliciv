import logging
import random
from typing import Dict, List

from thespian.actors import Actor, ActorExitRequest, WakeupMessage

from cliciv.messages import ResourcesRequest, Start, ResourcesRequestGranted, ResourcesRequestDenied, ResourcesProduced, \
    WorkerProfile, TechnologyProduced
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.utils.data import dict_from_data
from cliciv.utils.dicts import dict_apply_delta
from cliciv.utils.game_parameters import GameParameters

logger = logging.getLogger(__name__)


class _ProfileDictType(type):
    def __getitem__(cls, item):
        if not cls.ready:
            cls.load()
        return cls._DICT[item]


class Profiles(object, metaclass=_ProfileDictType):
    """
    dict-like type that loads occupation definitions once.

    Use as `Profiles['gatherer']`
    """
    _DICT = {}
    ready = False

    @staticmethod
    def load():
        for k, p in dict_from_data('occupations').items():
            logger.debug("Creating profile '{}' with data: {}".format(k, p))
            Profiles._DICT[k] = Profile(k, **(p or {}))

        Profiles.ready = True

    @classmethod
    def update(cls, research_id, profile_update) -> List[str]:
        updated = []
        for occupation, info in profile_update.items():
            profile: Profile = Profiles._DICT[occupation]
            if research_id in profile.upgrades:
                # Already got this upgrade
                continue

            profile.apply_upgrade(research_id, info)
            updated.append(occupation)

        return updated


class Profile(object):
    def __init__(self, occupation, needs=None, produces=None, **kwargs):
        self.occupation = occupation
        self.needs = needs or {}
        self.produces = produces or {}
        self.upgrades = []
        if kwargs:
            logger.warning("Ignoring unexpected profile parameters: {}".format(kwargs))

    def apply_upgrade(self, research_id, info):
        self.upgrades.append(research_id)
        if 'requires' in info:
            dict_apply_delta(self.needs, info['requires'])
        if 'produces' in info:
            dict_apply_delta(self.needs, info['produces'])


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
        self._epoch = 0  # Track to ensure stale wake-ups don't generate extra resources
        super(Worker, self).__init__()

    def receiveMessage(self, msg, sender):
        logger.info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, WorkerProfile):
            logger.debug("New profile: {}".format(msg.new_profile))
            self._profile = msg.new_profile
            self._epoch += 1
        elif isinstance(msg, Start) or (isinstance(msg, WakeupMessage) and msg.payload == self._epoch):
            self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
            self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
            self.start_work()
        elif isinstance(msg, WakeupMessage):
            logger.debug("Stale wakeup message, must have new profile")
            self.wakeupAfter(1, self._epoch)
        elif isinstance(msg, ResourcesRequestGranted):
            self.produce_output()
            self.wakeupAfter(1, self._epoch)
        elif isinstance(msg, ResourcesRequestDenied):
            logger.warning("Worker {} request for resources denied".format(self))
            self.wakeupAfter(1, self._epoch)
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

    def start_work(self):
        if not self._profile:
            logger.error("Starting work with no profile!")
            return

        self.send(self.resources_manager, ResourcesRequest(self._profile.needs))

    def produce_output(self):
        if not self._profile:
            logger.error("Producing output with no profile!")
            return

        self.send(self.resources_manager, ResourcesProduced(self._profile.produces))

        # Chance of generating some useful insight into their job
        if random.random() < GameParameters.CHANCE_OF_TECH:
            self.send(self.technology_manager, TechnologyProduced(self._profile.occupation))
