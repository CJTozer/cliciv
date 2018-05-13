from thespian.actors import Actor

from cliciv.game_data import GameData
from cliciv.messages import DisplayStart, DisplaySetup, ResourcesRegisterForUpdates, ResourcesNewState, \
    TechnologyRegisterForUpdates, TechnologyNewState


class DisplayHandler(Actor):
    def __init__(self):
        self.resources_manager: str = None
        self.technology_manager: str = None
        self.game_data: GameData = GameData()

    def receiveMessage(self, msg, sender: Actor):
        if isinstance(msg, DisplaySetup):
            self.resources_manager = msg.resource_manager
            self.technology_manager = msg.tech_manager
        elif isinstance(msg, DisplayStart):
            self.start()
        elif isinstance(msg, ResourcesNewState):
            self.game_data.resources = msg.new_state
        elif isinstance(msg, TechnologyNewState):
            self.game_data.technology = msg.new_state
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))

        if self.game_data.is_complete:
            self.show_state()

    def show_state(self) -> None:
        print("Population ({}/{}):".format(self.game_data.total_population, self.game_data.popcap))
        for occupation, num in self.game_data.visible_occupations.items():
            print("{}: {}".format(occupation, num))

        print("\nResources:")
        for resource, amount in self.game_data.visible_resources.items():
            print("{}: {}".format(resource, amount))

    def start(self):
        self.send(self.resources_manager, ResourcesRegisterForUpdates())
        self.send(self.technology_manager, TechnologyRegisterForUpdates())
