from collections import defaultdict

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

        # ...the resources list
        self._resources_list = MultiColumnListBox(
            10,  # Height
            ["<10", ">10"],
            [],
            titles=["Material", "Quantity"],
            name="res_list")

        # ...then the occupation list
        self._occupation_list = MultiColumnListBox(
            10, # Height
            ["<10", ">10"],
            [],
            titles=["Occupation", "Number"],
            name="pop_list")

        self.add_layout(layout)
        layout.add_widget(self._resources_list)
        layout.add_widget(self._occupation_list)
        layout.add_widget(Label("Some help text"))

        self.fix()

        # Colours
        self.palette["disabled"] = self.palette["field"]

    def _update(self, frame_no):
        # Refresh the list view if needed
        if frame_no - self._last_frame >= self.frame_update_count or self._last_frame == 0:
            self._last_frame = frame_no

            # Create the data to go in the multi-column list...
            last_occupation_selection = self._occupation_list.value
            last_occupation_start_line = self._occupation_list.start_line

            game_data: GameData = self._new_state_callback()
            resource_data = [
                ([resource, "{:.2f}".format(amount)], resource)
                for resource, amount in game_data.visible_resources.items()
            ]
            occupation_data = [
                ([occupation, "{}".format(number)], occupation)
                for occupation, number in game_data.visible_occupations.items()
            ]

            # Update the list and try to reset the last selection.
            self._resources_list.disabled = True
            self._resources_list.options = resource_data

            self._occupation_list.options = occupation_data
            self._occupation_list.value = last_occupation_selection
            self._occupation_list.start_line = last_occupation_start_line

        # Now redraw as normal
        super(MainDisplay, self)._update(frame_no)

    @property
    def frame_update_count(self):
        # Refresh once every 0.5 seconds by default.
        return 10
