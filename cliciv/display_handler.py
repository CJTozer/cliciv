from thespian.actors import Actor, ActorExitRequest

from cliciv.game_data import GameData
from cliciv.messages import ResourcesNewState, TechnologyNewState, WorkersNewState, Start, RegisterForUpdates, \
    DisplayUpdate
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager


class DisplayHandler(Actor):
    def __init__(self):
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self.worker_manager: Actor = None
        self.game_data: GameData = GameData()
        super(DisplayHandler, self).__init__()

    def receiveMessage(self, msg, sender: Actor):
        self.logger().info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, Start):
            self.start()
        elif isinstance(msg, DisplayUpdate):
            if self.game_data.is_complete:
                self.show_state()
            else:
                self.logger().warn("Received DisplayUpdate before game state is complete")

        elif isinstance(msg, ResourcesNewState):
            self.game_data.resources = msg.new_state
        elif isinstance(msg, TechnologyNewState):
            self.game_data.technology = msg.new_state
        elif isinstance(msg, WorkersNewState):
            self.game_data.workers = msg.new_state
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))


    def show_state(self) -> None:
        print("=============================")
        print("Population ({}/{}):".format(self.game_data.total_population, self.game_data.popcap))
        for occupation, num in self.game_data.visible_occupations.items():
            print("{}: {}".format(occupation, num))

        print("\nResources:")
        for resource, amount in self.game_data.visible_resources.items():
            print("{}: {}".format(resource, amount))

    def start(self):
        self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
        self.worker_manager = self.createActor(WorkerManager, globalName="worker_manager")

        self.send(self.resources_manager, RegisterForUpdates())
        self.send(self.technology_manager, RegisterForUpdates())
        self.send(self.worker_manager, RegisterForUpdates())
