import time
from typing import List

from cliciv.display_handler import DisplayHandler
from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.command_handler import CommandHandler
from cliciv.game_data import GameData
from cliciv.game_state_manager import GameStateManager
from cliciv.messages import Start, GameStateRequest
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


class Coordinator():
    def __init__(self):
        # self.actor_system = ActorSystem('multiprocTCPBase')
        self.actor_system = ActorSystem()
        self.command_handler = CommandHandler()
        self.display_handler = DisplayHandler()

        self.resource_manager: Actor = self.actor_system.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager: Actor = self.actor_system.createActor(TechnologyManager, globalName="technology_manager")
        self.game_state_manager: Actor = self.actor_system.createActor(GameStateManager, globalName="game_state_manager")
        self.worker_manager: Actor = self.actor_system.createActor(WorkerManager, globalName="worker_manager")
        self.actors: List[Actor] = [
            self.resource_manager,
            self.technology_manager,
            self.game_state_manager,
            self.worker_manager,
        ]

    def start_game(self):
        # Start the active actors
        self.actor_system.tell(self.game_state_manager, Start())
        self.actor_system.tell(self.worker_manager, Start())

    def end_game(self):
        for a in self.actors:
            self.actor_system.tell(a, ActorExitRequest())

    def update_display(self):
        game_data: GameData = self.actor_system.ask(self.game_state_manager, GameStateRequest())
        self.display_handler.update_display(game_data)
