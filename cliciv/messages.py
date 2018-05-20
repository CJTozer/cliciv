from abc import ABC


class ActorMessage(ABC):
    def __str__(self):
        return "{}({})".format(self.__class__.__name__, vars(self))


class Start(ActorMessage):
    pass


class InitialState(ActorMessage):
    def __init__(self, state):
        self.state = state


class RegisterForUpdates(ActorMessage):
    pass


class ResourcesRequest(ActorMessage):
    def __init__(self, resources):
        self.requested = resources


class ResourcesRequestGranted(ActorMessage):
    pass


class ResourcesRequestDenied(ActorMessage):
    pass


class ResourcesNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class ResourcesProduced(ActorMessage):
    def __init__(self, resources):
        self.produced = resources


class TechnologyNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class TechnologyProduced(ActorMessage):
    def __init__(self, area, amount=1):
        self.area = area
        self.amount = amount


class TechnologyResearched(ActorMessage):
    def __init__(self, research_id):
        self.research_id = research_id


class WorkersNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class WorkerChangeRequest(ActorMessage):
    def __init__(self, worker_type, increment):
        self.worker_type = worker_type
        self.increment = increment


class WorkerProfile(ActorMessage):
    def __init__(self, new_profile):
        self.new_profile = new_profile


class BuildingsNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class BuilderAssignRequest(ActorMessage):
    def __init__(self, building, increment):
        self.building = building
        self.increment = increment


class BuildingIncrement(ActorMessage):
    def __init__(self, building, building_increment):
        self.building = building
        self.building_increment = building_increment


class GameStateRequest(ActorMessage):
    pass


class GameStateUnavailable(ActorMessage):
    pass
