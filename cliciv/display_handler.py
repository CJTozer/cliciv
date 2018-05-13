from thespian.actors import Actor

from cliciv.game_data import GameData
from cliciv.messages import DisplayMessage, DisplayNewGameState


class DisplayHandler(Actor):
    def receiveMessage(self, msg: DisplayMessage, sender: Actor):
        if isinstance(msg, DisplayNewGameState):
            self.show_state(msg.game_data)

    def show_state(self, data: GameData) -> None:
        print("Population ({}/{}):".format(data.total_population, data.popcap))
        for occupation, num in data.visible_occupations.items():
            print("{}: {}".format(occupation, num))


        print("\nResources:")
        for resource, amount in data.visible_resources.items():
            print("{}: {}".format(resource, amount))
