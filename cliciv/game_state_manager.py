import logging

from thespian.actors import Actor, ActorExitRequest

from cliciv.game_data import GameData
from cliciv.messages import ResourcesNewState, TechnologyNewState, WorkersNewState, Start, RegisterForUpdates, \
    GameStateRequest, GameStateUnavailable, InitialState
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager
from cliciv.worker_manager import WorkerManager


logger = logging.getLogger(__name__)


class GameStateManager(Actor):
    def __init__(self):
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self.worker_manager: Actor = None
        self.game_data: GameData = GameData()
        super(GameStateManager, self).__init__()

    def receiveMessage(self, msg, sender: Actor):
        logger.info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, Start):
            self.start()
        elif isinstance(msg, ResourcesNewState):
            self.game_data.resources = msg.new_state
        elif isinstance(msg, TechnologyNewState):
            self.game_data.technology = msg.new_state
        elif isinstance(msg, WorkersNewState):
            self.game_data.workers = msg.new_state
        elif isinstance(msg, GameStateRequest):
            if self.game_data.is_complete:
                self.send(sender, self.game_data)
            else:
                self.send(sender, GameStateUnavailable())
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

    def start(self):
        self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
        self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
        self.worker_manager = self.createActor(WorkerManager, globalName="worker_manager")

        new_game_state = {
            'technology': {
                'unlocked_occupations': ['gatherer', 'woodcutter'],
                'unlocked_materials': ['food', 'wood'],
            }
        }
        self.send(self.technology_manager, InitialState(new_game_state))

        self.send(self.resources_manager, RegisterForUpdates())
        self.send(self.technology_manager, RegisterForUpdates())
        self.send(self.worker_manager, RegisterForUpdates())
