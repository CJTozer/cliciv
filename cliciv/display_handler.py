from asciimatics.exceptions import ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, Label, MultiColumnListBox, Widget

from cliciv.game_data import GameData


class DisplayHandler(object):
    def __init__(self, new_state_callback):
        self._new_state_callback = new_state_callback

    def do_display(self) -> None:
        while True:
            try:
                Screen.wrapper(self._main_display)
            except ResizeScreenError:
                pass

    def _main_display(self, screen):
        frame = MainDisplay(screen, self._new_state_callback)
        scene = Scene([frame], -1)
        screen.play([scene])


class MainDisplay(Frame):
    def __init__(self, screen, new_state_callback):
        super(MainDisplay, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          title="Main Display",
                                          name="Main Display")

        # Internal state required for doing periodic updates
        self._last_frame = 0
        self._new_state_callback = new_state_callback

        # Create the basic form layout...
        layout = Layout([1], fill_frame=True)
        self._list = MultiColumnListBox(
            Widget.FILL_FRAME,
            ["<10", "<10"],
            [],
            titles=["Material", "Quantity"],
            name="pop_list")

        self.add_layout(layout)
        layout.add_widget(self._list)
        layout.add_widget(
            Label("Some help text"))
        self.fix()

        # Add my own colour palette
        # self.palette = defaultdict(
        #     lambda: (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK))
        # for key in ["selected_focus_field", "label"]:
        #     self.palette[key] = (Screen.COLOUR_WHITE, Screen.A_BOLD, Screen.COLOUR_BLACK)
        # self.palette["title"] = (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE)

    def _update(self, frame_no):
        # Refresh the list view if needed
        if frame_no - self._last_frame >= self.frame_update_count or self._last_frame == 0:
            self._last_frame = frame_no

            # Create the data to go in the multi-column list...
            last_selection = self._list.value
            last_start = self._list.start_line

            game_data: GameData = self._new_state_callback()
            new_data = [
                ([resource, "{}".format(amount)], resource)
                for resource, amount in game_data.visible_resources.items()
            ]

            # row = 0
            # self.screen.print_at("Population ({}/{}):".format(game_data.total_population, game_data.popcap),
            #                      0, row)
            # row += 1
            # for occupation, num in game_data.visible_occupations.items():
            #     self.screen.print_at("{}: {}".format(occupation, num),
            #                          2, row)
            #     row += 1
            #
            # row += 1
            # self.screen.print_at("Resources:", 0, row)
            # row += 1
            # for resource, amount in game_data.visible_resources.items():
            #     self.screen.print_at("{}: {}".format(resource, amount),
            #                          2, row)
            #     row += 1

            # Update the list and try to reset the last selection.
            self._list.options = new_data
            self._list.value = last_selection
            self._list.start_line = last_start

        # Now redraw as normal
        super(MainDisplay, self)._update(frame_no)

    @property
    def frame_update_count(self):
        # Refresh once every 0.5 seconds by default.
        return 10
