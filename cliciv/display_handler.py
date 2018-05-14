class DisplayHandler(object):
    def __init__(self):
        self.screen = None

    def update_display(self, game_data) -> None:
        if not self.screen:
            return

        self.screen.clear()

        row = 0
        self.screen.print_at("Population ({}/{}):".format(game_data.total_population, game_data.popcap),
                             0, row)
        row += 1
        for occupation, num in game_data.visible_occupations.items():
            self.screen.print_at("{}: {}".format(occupation, num),
                                 2, row)
            row += 1

        row += 1
        self.screen.print_at("Resources:", 0, row)
        row += 1
        for resource, amount in game_data.visible_resources.items():
            self.screen.print_at("{}: {}".format(resource, amount),
                                 2, row)
            row += 1

        self.screen.refresh()

    def set_screen(self, screen):
        self.screen = screen
