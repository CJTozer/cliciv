from collections import OrderedDict
from typing import Dict

from cliciv.technology_manager import TechnologyManager
from cliciv.resource_manager import ResourceManager


class Resources(object):
    @property
    def materials():
        return {
            "food": 1.0,
            "water": 2.0,
            "wood": 2.6,
            "stone": 0.0,
        }


class Technology(object):
    @property
    def unlocked_materials():
        return ["food", "wood"]

    @property
    def unlocked_occupations():
        return ["idle", "gatherer", "builder"]


class GameData(object):
    def __init__(self, resources: Resources =None, tech: Technology = None):
        self.resources = resources
        self.technology = tech

    @property
    def is_complete(self):
        return all([
            self.resources is not None,
            self.technology is not None,
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
            (k, self.resources.occupations.get(k, 0))
            for k in self.technology.unlocked_occupations
        ])

    @property
    def total_population(self) -> int:
        return sum(self.visible_occupations.values())

    @property
    def popcap(self) -> int:
        return 10
