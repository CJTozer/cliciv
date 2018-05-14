from abc import ABC

from thespian.actors import Actor


class ActorMessage(ABC):
    def __str__(self):
        return self.__class__.__name__


class DisplaySetup(ActorMessage):
    def __init__(self,
                 resource_manager: Actor,
                 technology_manager: Actor,
                 worker_manager: Actor):
        self.resource_manager = resource_manager
        self.technology_manager = technology_manager
        self.worker_manager = worker_manager


class DisplayStart(ActorMessage):
    pass


class WorkerManagerSetup(ActorMessage):
    def __init__(self,
                 resource_manager: Actor,
                 technology_manager: Actor):
        self.resource_manager = resource_manager
        self.technology_manager = technology_manager


class WorkersStart(ActorMessage):
    pass


class WorkerSetup(ActorMessage):
    def __init__(self,
                 resource_manager: str,
                 technology_manager: str):
        self.resource_manager = resource_manager
        self.technology_manager = technology_manager


class WorkerStart(ActorMessage):
    pass


class ResourcesRegisterForUpdates(ActorMessage):
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


class TechnologyRegisterForUpdates(ActorMessage):
    pass


class TechnologyNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state


class WorkersRegisterForUpdates(ActorMessage):
    pass


class WorkersNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state
