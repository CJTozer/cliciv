class DisplayHandler(object):

    def update_display(self, game_data) -> None:
        print("=============================")
        print("Population ({}/{}):".format(game_data.total_population, game_data.popcap))
        for occupation, num in game_data.visible_occupations.items():
            print("{}: {}".format(occupation, num))

        print("\nResources:")
        for resource, amount in game_data.visible_resources.items():
            print("{}: {}".format(resource, amount))

# def demo(screen):
#     screen.print_at('Hello world!', 0, 0)
#     screen.refresh()
#     time.sleep(5)
#     screen.print_at('Hello world!', 5, 0)
#     screen.refresh()
#     time.sleep(5)
#
# Screen.wrapper(demo)

