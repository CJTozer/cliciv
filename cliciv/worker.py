from typing import Dict

from thespian.actors import Actor, ActorExitRequest, WakeupMessage

from cliciv.messages import ResourcesRequest, Start, ResourcesRequestGranted, ResourcesRequestDenied, ResourcesProduced
from cliciv.resource_manager import ResourceManager
from cliciv.technology_manager import TechnologyManager


class WorkerFactory():
    def __init__(self, worker_manager: Actor):
        self.worker_manager = worker_manager
        super(WorkerFactory, self).__init__()

    def from_config(self, config: Dict[str, int]):
        return {
            occupation: self.generate_n(occupation, num)
            for occupation, num in config.items()
        }

    def generate_n(self, occupation: str, num: int):
        return [
            self.of_type(occupation) for _ in range(num)
        ]

    def of_type(self, occupation: str):
        mapping = {
            'idle': Idler,
            'gatherer': Gatherer
        }
        return self.worker_manager.createActor(mapping.get(occupation))


class Worker(Actor):
    def __init__(self):
        self.resources_manager: Actor = None
        self.technology_manager: Actor = None
        super(Worker, self).__init__()
    
    def receiveMessage(self, msg, sender):
        self.logger().info("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, Start) or isinstance(msg, WakeupMessage):
            self.resources_manager = self.createActor(ResourceManager, globalName="resource_manager")
            self.technology_manager = self.createActor(TechnologyManager, globalName="technology_manager")
            self.start_work()
        elif isinstance(msg, ResourcesRequestGranted):
            self.produce_output()
            self.wakeupAfter(1)
        elif isinstance(msg, ResourcesRequestDenied):
            self.logger().warn("Worker {} request for resources denied".format(self))
            self.wakeupAfter(1)
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))

    def start_work(self):
        raise NotImplementedError("Worker subclass must define start_work")

    def produce_output(self):
        raise NotImplementedError("Worker subclass must define produce_output")


class Idler(Worker):
    def start_work(self):
        # Idle - only needs a small amount of food
        req = {'food': 0.5}
        self.send(self.resources_manager, ResourcesRequest(req))

    def produce_output(self):
        # Idleness creates nothing
        pass


class Gatherer(Worker):
    def start_work(self):
        # Gatherer - requires full rations
        req = {'food': 1.0}
        self.send(self.resources_manager, ResourcesRequest(req))

    def produce_output(self):
        # Gather 1.25 food per day
        produced = {'food': 1.25}
        self.send(self.resources_manager, ResourcesProduced(produced))
