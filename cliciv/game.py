import time
from typing import List

from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.messages import Start
from cliciv.command_handler import CommandHandler
from cliciv.game_state_manager import GameStateManager
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager


class Game(object):
    def __init__(self):
        self.coordinator = Coordinator()

    def play(self):
        self.coordinator.start_game()
        for _ in range(10):
            self.coordinator.update_display()
            time.sleep(0.5)
        self.coordinator.end_game()


    # def demo(screen):
    #     screen.print_at('Hello world!', 0, 0)
    #     screen.refresh()
    #     time.sleep(5)
    #     screen.print_at('Hello world!', 5, 0)
    #     screen.refresh()
    #     time.sleep(5)
    #
    # Screen.wrapper(demo)

    # def update_display(self) -> None:
    #     print("=============================")
    #     print("Population ({}/{}):".format(self.game_data.total_population, self.game_data.popcap))
    #     for occupation, num in self.game_data.visible_occupations.items():
    #         print("{}: {}".format(occupation, num))
    #
    #     print("\nResources:")
    #     for resource, amount in self.game_data.visible_resources.items():
    #         print("{}: {}".format(resource, amount))


class Coordinator():
    def __init__(self):
        # self.actor_system = ActorSystem('multiprocTCPBase')
        self.actor_system = ActorSystem()
        self.command_handler = CommandHandler()

        self.resource_manager: Actor = self.actor_system.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager: Actor = self.actor_system.createActor(TechnologyManager, globalName="technology_manager")
        self.display_handler: Actor = self.actor_system.createActor(GameStateManager, globalName="display_handler")
        self.worker_manager: Actor = self.actor_system.createActor(WorkerManager, globalName="worker_manager")
        self.actors: List[Actor] = [
            self.resource_manager,
            self.technology_manager,
            self.display_handler,
            self.worker_manager,
        ]

    def start_game(self):
        # Start the active actors
        self.actor_system.tell(self.display_handler, Start())
        self.actor_system.tell(self.worker_manager, Start())

    def end_game(self):
        for a in self.actors:
            self.actor_system.tell(a, ActorExitRequest())

    def update_display(self):
        pass
