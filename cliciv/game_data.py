import logging
from collections import OrderedDict
from typing import Dict

from cliciv.building_manager import BuildingState
from cliciv.resource_manager import ResourceState
from cliciv.technology_manager import TechnologyState
from cliciv.worker_manager import WorkerState

logger = logging.getLogger(__name__)


class GameData(object):
    def __init__(self,
                 resources: ResourceState=None,
                 technology: TechnologyState=None,
                 workers: WorkerState=None,
                 buildings: BuildingState=None):
        self.resources = resources
        self.technology = technology
        self.workers = workers
        self.buildings = buildings

    @property
    def is_complete(self):
        return all([
            self.resources,
            self.technology,
            self.workers,
            self.buildings,
        ])

    @property
    def visible_resources(self) -> Dict[str, float]:
        # Maintain ordering from `unlocked_resources`
        return OrderedDict([
            (k, self.resources.resources.get(k, 0.0))
            for k in self.technology.unlocked_resources
        ])

    @property
    def visible_occupations(self) -> Dict[str, int]:
        return OrderedDict([
            (k, self.workers.occupations.get(k, 0))
            for k in self.technology.unlocked_occupations
        ])

    @property
    def total_population(self) -> int:
        return sum(self.visible_occupations.values())

    @property
    def popcap(self) -> int:
        return 10
