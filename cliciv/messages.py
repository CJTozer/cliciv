class DisplayMessage(object):
    pass


class DisplayNewGameState(DisplayMessage):
    def __init__(self, game_data):
        self.game_data = game_data
