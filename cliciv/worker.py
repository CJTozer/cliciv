from typing import Dict

from thespian.actors import Actor, ActorExitRequest

from cliciv.messages import ResourcesRequest, WorkerStart, ResourcesRequestGranted, WorkerSetup


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
        # mapping = {
        #     'idle': IdleWorker
        # }
        # return mapping.get(occupation)
        return self.worker_manager.createActor(IdleWorker)


class Worker(Actor):
    def __init__(self):
        self.resources_manager = None
        self.technology_manager = None
        super(Worker, self).__init__()
    
    def receiveMessage(self, msg, sender):
        self.logger().warn("{}/{}".format(msg, self))
        if isinstance(msg, ActorExitRequest):
            pass
        elif isinstance(msg, WorkerSetup):
            self.resources_manager = msg.resource_manager
            self.technology_manager = msg.technology_manager
        elif isinstance(msg, WorkerStart):
            self.start_work()
        elif isinstance(msg, ResourcesRequestGranted):
            self.produce_output()
            self.wakeupAfter(1)
        else:
            self.logger().error("Ignoring unexpected message: {}".format(msg))

    def start_work(self):
        raise NotImplementedError("Worker subclass must define start_work")

    def produce_output(self):
        raise NotImplementedError("Worker subclass must define produce_output")


class IdleWorker(Worker):
    def start_work(self):
        # Idle - only needs a small amount of food
        req = {'food': 0.5}
        self.send(self.resources_manager, ResourcesRequest(req))

    def produce_output(self):
        # Idleness creates nothing
        pass
