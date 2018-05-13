from typing import Dict

class ResourceManager(object):
    @property
    def resources(self) -> Dict[str, float]:
        return {
            "food": 1.0,
            "wood": 2.6,
            "stone": 0.0,
        }

