from abc import ABC


class ActorMessage(ABC):
    pass


class DisplaySetup(ActorMessage):
    def __init__(self,
                 resource_manager: str,
                 tech_manager: str):
        self.resource_manager = resource_manager
        self.tech_manager = tech_manager


class DisplayStart(ActorMessage):
    pass


class CoordinatorMessage(ActorMessage):
    pass


class CoordinatorGetResourcesmanager(ActorMessage):
    pass


class ResourcesMessage(ActorMessage):
    pass


class ResourcesRegisterForUpdates(ActorMessage):
    pass

class ResourcesNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state
