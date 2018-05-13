from cliciv.command_handler import CommandHandler
from cliciv.display_handler import DisplayHandler
from cliciv.game_data import GameData


class Game(object):
    def __init__(self):
        self.game_data = GameData()
        self.command_handler = CommandHandler()
        self.display_handler = DisplayHandler()

    def play(self):
        self.display_handler.show_state(self.game_data)
