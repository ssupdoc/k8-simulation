from abc import ABC, abstractmethod

class LoadBalancerQueue:
    def __init__(self, pod, priority):
        self.pod = pod
        self.priority = priority

class AbstractLoadBalancer(ABC):
    def AssignPod(self, request, pod):
        pod.HandleRequest(request)
    @abstractmethod
    def FindPod(self):
        raise NotImplementedError
    @abstractmethod
    def UpdatePodList(self):
        raise NotImplementedError
    @abstractmethod
    def FindPriorityQueueItem(self):
        raise NotImplementedError