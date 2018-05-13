from abc import ABC

from thespian.actors import Actor


class ActorMessage(ABC):
    pass


class GenericSetup(ActorMessage):
    def __init__(self,
                 resource_manager: Actor,
                 tech_manager: Actor):
        self.resource_manager = resource_manager
        self.technology_manager = tech_manager


class DisplaySetup(GenericSetup):
    pass


class DisplayStart(ActorMessage):
    pass


class WorkerManagerSetup(GenericSetup):
    pass


class ResourcesRegisterForUpdates(ActorMessage):
    pass


class ResourcesRequest(ActorMessage):
    def __init__(self, resources):
        self.requested = resources


class ResourcesRequestGrant(ActorMessage):
    def __init__(self, resources):
        self.granted = resources


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
