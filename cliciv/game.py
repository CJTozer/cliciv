import time
from typing import List

from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.messages import Start, DisplayUpdate
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager


class Game(object):
    def __init__(self):
        self.coordinator = Coordinator()

    def play(self):
        self.coordinator.start_game()
        for _ in range(100):
            self.coordinator.update_display()
            time.sleep(0.1)
        self.coordinator.end_game()


class Coordinator():
    def __init__(self):
        # self.actor_system = ActorSystem('multiprocTCPBase', logDefs=self.logging_config())
        self.actor_system = ActorSystem()#logDefs=self.logging_config())
        self.command_handler = CommandHandler()

        self.resource_manager: Actor = self.actor_system.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager: Actor = self.actor_system.createActor(TechnologyManager, globalName="technology_manager")
        self.display_handler: Actor = self.actor_system.createActor(DisplayHandler, globalName="display_handler")
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

    def logging_config(self):
        # See https://docs.python.org/3.6/library/logging.config.html#logging-config-dictschema
        return {
            'version': 1,
            # 'incremental': True,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'DEBUG',
                    'stream': 'ext://sys.stdout'
                }
            }
        }

    def update_display(self):
        self.actor_system.tell(self.display_handler, DisplayUpdate())
