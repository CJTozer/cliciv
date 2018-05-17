import logging
from collections import OrderedDict
from typing import Dict

from cliciv.resource_manager import ResourceState
from cliciv.technology_manager import TechnologyState
from cliciv.worker_manager import WorkerState

logger = logging.getLogger(__name__)


class GameData(object):
    def __init__(self,
                 resources: ResourceState={},
                 technology: TechnologyState={},
                 workers: WorkerState={}):
        self.resources = resources
        self.technology = technology
        self.workers = workers

    @property
    def is_complete(self):
        return all([
            self.resources,
            self.technology,
            self.workers,
        ])

    @property
    def visible_resources(self) -> Dict[str, float]:
        # Maintain ordering from `unlocked_resources`
        return OrderedDict([
            (k, self.resources.materials.get(k, 0.0))
            for k in self.technology.unlocked_materials
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
