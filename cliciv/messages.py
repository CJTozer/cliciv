from abc import ABC


class ActorMessage(ABC):
    def __str__(self):
        return self.__class__.__name__


class Start(ActorMessage):
    pass


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


class TechnologyNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class WorkersNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state
