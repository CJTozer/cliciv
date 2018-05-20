import logging

from thespian.actors import Actor

from cliciv.messages import InitialState, RegisterForUpdates, TechnologyNewState, BuildingsNewState, \
    BuildingIncrement, BuildersAssigned, BuilderAssignRequest

logger = logging.getLogger(__name__)


class BuildingManager(Actor):
    def __init__(self):
        self.started = False
        self.registered = []
        self.worker_manager = None
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
        elif isinstance(msg, BuildersAssigned):
            self.worker_manager = sender
            if msg.building_id not in self.building_state.under_construction:
                logger.warning("Assigning builders to building not under construction: {}".format(msg.building_id))
                self.send(self.worker_manager, BuilderAssignRequest(msg.building_id, -msg.num_builders))
                return
            self.building_state.under_construction[msg.building_id]['builders'] = msg.num_builders
            notify_change = True
        elif isinstance(msg, BuildingIncrement):
            building_complete, info = self._handle_building_increment(msg.building_id, msg.building_increment)
            # Cancel builders when building complete.
            if building_complete:
                self._handle_building_complete(msg.building_id, info)
            notify_change = True
        else:
            logger.error("Ignoring unexpected message: {}".format(msg))

        if notify_change:
            for actor in self.registered:
                self.send(actor, BuildingsNewState(self.building_state))

    def _handle_tech_update(self, new_state):
        pass

    def _handle_building_increment(self, building_id, increment):
        if building_id not in self.building_state.under_construction:
            logger.debug("Received more work on already completed building {}".format(building_id))
            return False, None
        info = self.building_state.under_construction[building_id]
        if 'building_done' not in info:
            info['building_done'] = 0
        info['building_done'] += increment
        if info['building_done'] >= info['building_required']:
            # Construction complete!
            self.building_state.under_construction.pop(building_id)
            old_val = self.building_state.completed.get(info['type'], 0)
            self.building_state.completed[info['type']] = old_val + 1
            return True, info

        return False, None

    def _handle_building_complete(self, building_id, info):
        # Free up the workers building the building
        self.send(self.worker_manager, BuilderAssignRequest(building_id, -info['builders']))

class BuildingState(object):
    def __init__(self, initial_buildings):
        self.__dict__ = initial_buildings
