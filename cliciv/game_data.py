from collections import OrderedDict
from typing import Dict

from cliciv.TechnologyManager import TechnologyManager
from cliciv.resource_manager import ResourceManager


class GameData(object):
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.tech_manager = TechnologyManager()

    @property
    def visible_resources(self) -> Dict[str, float]:
        # Maintain ordering from `unlocked_resources`
        return OrderedDict([
            (k, self.resource_manager.resources.get(k, 0.0))
            for k in self.tech_manager.unlocked_resources
        ])

    @property
    def visible_occupations(self) -> Dict[str, int]:
        return OrderedDict([
            (k, self.resource_manager.occupations.get(k, 0))
            for k in self.tech_manager.unlocked_occupations
        ])

    @property
    def total_population(self) -> int:
        return sum(self.visible_occupations.values())

    @property
    def popcap(self) -> int:
        return 10
