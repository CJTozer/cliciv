import logging

from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.widgets import Frame, Layout, Label, MultiColumnListBox, Divider, ListBox, TextBox

from cliciv.command_handler import CommandType
from cliciv.game_data import GameData
from cliciv.messages import GameStateUnavailable

logger = logging.getLogger(__name__)


class DisplayHandler(object):
    def __init__(self, new_state_callback, command_handler):
        self.new_state_callback = new_state_callback
        self.command_handler = command_handler

    def do_display(self) -> None:
        while True:
            try:
                Screen.wrapper(self._main_display, catch_interrupt=True)
                return
            except ResizeScreenError:
                pass

    def _main_display(self, screen):
        frame = MainDisplay(screen, self)
        scene = Scene([frame], -1)
        screen.play([scene])


class MainDisplay(Frame):
    def __init__(self, screen, display_handler):
        super(MainDisplay, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          title="Main Display",
                                          name="Main Display")

        # Internal state required for doing periodic updates
        self._last_frame = 0
        self._dh: DisplayHandler = display_handler
        self._game_data: GameData = None

        # Create the resources view layout...
        status_layout = Layout([1, 1], fill_frame=False)

        # ...the resources list
        self._resources_list = MultiColumnListBox(
            10,  # Height
            ["<12", ">10"],
            [],
        )
        self._is_tab_stop = False

        # ...then the occupation list
        self._occupation_list = MultiColumnListBox(
            10,  # Height
            ["<12", ">10"],
            [],
        )

        self.add_layout(status_layout)
        status_layout.add_widget(Label("Resources"), column=0)
        status_layout.add_widget(self._resources_list, column=0)
        status_layout.add_widget(Label("Workers"), column=1)
        status_layout.add_widget(self._occupation_list, column=1)

        # Create a layout for research
        research_layout = Layout([1, 1], fill_frame=False)

        # ...list of available research
        self._available_research = ListBox(
            10,
            [],
            on_change=self._on_research_selected
        )

        self.add_layout(research_layout)
        research_layout.add_widget(Divider(), column=0)
        research_layout.add_widget(Label("Available Research"), column=0)
        research_layout.add_widget(self._available_research, column=0)
        research_layout.add_widget(Divider(), column=1)

        # Create a layout for help text at the bottom
        help_layout = Layout([1], fill_frame=True)
        self.add_layout(help_layout)
        help_layout.add_widget(Divider())

        # ...the help widget itself
        self._help = TextBox(height=3, label="Help: ", as_string=True)
        self._help.value = "TEST"
        # self._help.custom_colour = 'title'
        help_layout.add_widget(self._help)
        help_layout.add_widget(Divider())

        self.fix()

        # Colours
        self.palette["disabled"] = self.palette["field"]

    def _update(self, frame_no):
        # Refresh the list view if needed
        if frame_no - self._last_frame >= self.frame_update_count or self._last_frame == 0:
            self._last_frame = frame_no

            # Get up-to-date data
            self._game_data = self._dh.new_state_callback()

            if isinstance(self._game_data, GameStateUnavailable):
                logger.info("Game state not yet available")
            else:
                # Resources list
                resource_data = [
                    ([resource, "{:.2f}".format(amount)], resource)
                    for resource, amount in self._game_data.visible_resources.items()
                ]
                self._resources_list.disabled = True
                self._resources_list.options = resource_data

                # Occupation list
                last_selection = self._occupation_list.value
                occupation_data = [
                    ([occupation, "{}".format(number)], occupation)
                    for occupation, number in self._game_data.visible_occupations.items()
                ]
                self._occupation_list.options = occupation_data
                self._occupation_list.value = last_selection

                # Research available list
                last_selection = self._available_research.value
                research_available = [
                    (info['name'], key)
                    for key, info in self._game_data.technology.unlocked_research.items()
                ]
                self._available_research.options = research_available
                self._available_research.value = last_selection

        # Now redraw as normal
        super(MainDisplay, self)._update(frame_no)

    def _on_research_selected(self):
        research_id = self._available_research.value
        if not research_id:
            return
        research_info = self._game_data.technology.unlocked_research[research_id]
        self._help.value = research_info.get('help', 'No help available for research item {}'.format(research_id))

    @property
    def frame_update_count(self):
        # Refresh once every 0.5 seconds by default.
        return 10

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            logger.debug("Keyboard event: {}".format(event.key_code))
            if event.key_code in [Screen.ctrl("c")]:
                raise StopApplication("User quit")
            elif event.key_code == ord("+"):
                if self._occupation_list.value:
                    self._dh.command_handler.increment(
                        CommandType.OCCUPATIONS,
                        self._occupation_list.value,
                        1
                    )
            elif event.key_code == ord("-"):
                if self._occupation_list.value:
                    self._dh.command_handler.increment(
                        CommandType.OCCUPATIONS,
                        self._occupation_list.value,
                        -1
                    )
            elif event.key_code in (ord("r"), ord("R")):
                if self._available_research.value:
                    self._dh.command_handler.research(
                        self._available_research.value,
                    )

        # Force a refresh for responsive UI
        self._last_frame = 0

        # Now pass on to lower levels for normal handling of the event.
        return super(MainDisplay, self).process_event(event)
