from cliciv.game_data import GameData


class DisplayHandler(object):
    def show_state(self, data: GameData) -> None:
        for resource, amount in data.visible_resources.items():
            print("{}: {}".format(resource, amount))
