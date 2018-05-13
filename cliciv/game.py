from thespian.actors import ActorSystem, ActorExitRequest

from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.game_data import GameData
from cliciv.messages import DisplayNewGameState


class Game(object):
    def __init__(self):
        self.actor_system = ActorSystem()
        self.game_data = GameData()
        self.command_handler = CommandHandler()
        self.display_handler = self.actor_system.createActor(DisplayHandler)

    def play(self):
        self.actor_system.tell(self.display_handler, DisplayNewGameState(self.game_data))

    def end(self):
        self.actor_system.tell(self.display_handler, ActorExitRequest())

