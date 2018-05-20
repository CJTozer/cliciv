import logging
from typing import List

from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.game_data import GameData
from cliciv.game_state_manager import GameStateManager
from cliciv.messages import Start, GameStateRequest
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager

logging.basicConfig(level=logging.INFO,
                    filename='/tmp/cliciv-debug.log',
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


class Game(object):
    def __init__(self):
        self.coordinator = Coordinator()

    def play(self):
        self.coordinator.start_game()
        self.coordinator.end_game()


class Coordinator():
    def __init__(self):
        self.actor_system = ActorSystem('multiprocQueueBase')
        self.command_handler = CommandHandler(self)
        self.display_handler = DisplayHandler(self.get_new_game_data, self.command_handler)

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

        # Call into display manager - this is completely blocking
        self.display_handler.do_display()

    def end_game(self):
        for a in self.actors:
            self.actor_system.tell(a, ActorExitRequest())

    def get_new_game_data(self) -> GameData:
        return self.actor_system.ask(self.game_state_manager, GameStateRequest())
