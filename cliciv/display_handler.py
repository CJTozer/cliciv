from cliciv.game_data import GameData


class DisplayHandler(object):
    def show_state(self, data: GameData) -> None:
        print("Population ({}/{}):".format(data.total_population, data.popcap))
        for occupation, num in data.visible_occupations.items():
            print("{}: {}".format(occupation, num))


        print("\nResources:")
        for resource, amount in data.visible_resources.items():
            print("{}: {}".format(resource, amount))
