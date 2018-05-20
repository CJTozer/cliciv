import logging

from thespian.actors import Actor

from cliciv.messages import InitialState, RegisterForUpdates, TechnologyNewState, BuildingsNewState, \
    BuilderAssignRequest, BuildingIncrement

logger = logging.getLogger(__name__)


class BuildingManager(Actor):
    def __init__(self):
        self.started = False
        self.registered = []
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        self.worker_manager: Actor = None
        self.building_state: BuildingState = None
        super(BuildingManager, self).__init__()

    def receiveMessage(self, msg, sender: str):
        logger.info("{}/{}".format(msg, self))
        notify_change = False

        if isinstance(msg, InitialState):
            self.building_state = BuildingState(msg.state['buildings'])
        elif isinstance(msg, RegisterForUpdates):
            # `ActorAddress` can't be hashed, so can't just use set() here
            if sender not in self.registered:
                self.registered.append(sender)
            self.send(sender, BuildingsNewState(self.building_state))
        elif isinstance(msg, TechnologyNewState):
            self._handle_tech_update(msg.new_state)
            self.building_state = msg.new_state
        elif isinstance(msg, BuilderAssignRequest):
            pass
        elif isinstance(msg, BuildingIncrement):
            pass
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

        if notify_change:
            for actor in self.registered:
                self.send(actor, BuildingsNewState(self.building_state))

    def _handle_tech_update(self, new_state):
        pass


class BuildingState(object):
    def __init__(self, initial_buildings):
        self.__dict__ = initial_buildings
