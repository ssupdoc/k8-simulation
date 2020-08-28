from abc import ABC, abstractmethod
class AbstractLoadBalancer(ABC):
    def AssignPod(self, request, pod):
        pod.HandleRequest(request)
    @abstractmethod
    def FindPod(self):
        raise NotImplementedError