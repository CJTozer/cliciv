from thespian.actors import ActorSystem, ActorExitRequest, Actor

from cliciv.technology_manager import TechnologyManager
from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.messages import DisplayStart, DisplaySetup
from cliciv.resource_manager import ResourceManager


class Game(object):
    def __init__(self):
        self.coordinator = Coordinator()

    def play(self):
        self.coordinator.start_game()

    def end(self):
        self.coordinator.end_game()


class Coordinator():
    def __init__(self):
        self.actor_system = ActorSystem()
        self.command_handler = CommandHandler()

        self.resource_manager: Actor = self.actor_system.createActor(ResourceManager)
        self.tech_manager: Actor = self.actor_system.createActor(TechnologyManager)
        self.display_handler: Actor = self.actor_system.createActor(DisplayHandler)


    def start_game(self):
        # Tell the display handler about the sources it needs
        self.actor_system.tell(self.display_handler,
                               DisplaySetup(self.resource_manager,
                                            self.tech_manager))
        self.actor_system.tell(self.display_handler,
                               DisplayStart())

    def end_game(self):
        self.actor_system.tell(self.display_handler, ActorExitRequest())
