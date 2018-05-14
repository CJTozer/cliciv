from typing import List

import time
from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.messages import DisplayStart, DisplaySetup, WorkerManagerSetup, WorkersStart
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager


class Game(object):
    def __init__(self):
        self.coordinator = Coordinator()

    def play(self):
        self.coordinator.start_game()
        time.sleep(5)
        self.coordinator.end_game()


class Coordinator():
    def __init__(self):
        # self.actor_system = ActorSystem('multiprocTCPBase', logDefs=self.logging_config())
        self.actor_system = ActorSystem()#logDefs=self.logging_config())
        self.command_handler = CommandHandler()

        self.resource_manager: Actor = self.actor_system.createActor(ResourceManager)
        self.tech_manager: Actor = self.actor_system.createActor(TechnologyManager)
        self.display_handler: Actor = self.actor_system.createActor(DisplayHandler)
        self.worker_manager: Actor = self.actor_system.createActor(WorkerManager)
        self.actors: List[Actor] = [
            self.resource_manager,
            self.tech_manager,
            self.display_handler,
        ]

    def start_game(self):
        # Tell the display handler about the sources it needs
        self.actor_system.tell(self.display_handler,
                               DisplaySetup(self.resource_manager,
                                            self.tech_manager,
                                            self.worker_manager))

        # Tell the worker manager about the sources it needs
        self.actor_system.tell(self.worker_manager,
                               WorkerManagerSetup(self.resource_manager,
                                                  self.tech_manager))

        # Start the active actors
        self.actor_system.tell(self.display_handler,
                               DisplayStart())
        self.actor_system.tell(self.worker_manager,
                               WorkersStart())

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
