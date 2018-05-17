from abc import ABC


class ActorMessage(ABC):
    def __str__(self):
        return "{}({})".format(self.__class__.__name__, vars(self))


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


class ResourcesProduced(ActorMessage):
    def __init__(self, resources):
        self.produced = resources


class TechnologyNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


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


class GameStateRequest(ActorMessage):
    pass


class GameStateUnavailable(ActorMessage):
    pass
