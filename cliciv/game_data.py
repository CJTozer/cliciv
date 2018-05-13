from typing import Dict

from cliciv.resource_manager import ResourceManager


class GameData(object):
    def __init__(self):
        self.unlocked_resources = ["food", "wood"]
        self.resource_manager = ResourceManager()

    @property
    def visible_resources(self) -> Dict[str, float]:
        return {
            k: v
            for k, v in self.resource_manager.resources.items()
            if k in self.unlocked_resources
        }
