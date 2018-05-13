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


class ResourcesRegisterForUpdates(ActorMessage):
    pass

class ResourcesNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state

class TechnologyRegisterForUpdates(ActorMessage):
    pass

class TechnologyNewState(ActorMessage):
    def __init__(self, new_state):
        self.new_state = new_state
