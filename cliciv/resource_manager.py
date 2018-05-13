from typing import Dict

class ResourceManager(object):
    def __init__(self):
        self.population = []

    @property
    def occupations(self) -> Dict[str, int]:
        return {
            "gatherer": 2,
            "idle": 3,
            "builder": 0,
            "woodcutter": 1,
        }

    @property
    def resources(self) -> Dict[str, float]:
        return {
            "food": 1.0,
            "water": 2.0,
            "wood": 2.6,
            "stone": 0.0,
        }
