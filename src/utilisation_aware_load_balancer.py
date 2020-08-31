from src.abstract_load_balancer import AbstractLoadBalancer, LoadBalancerQueue

class UtilisationAwareLoadBalancer(AbstractLoadBalancer):
    def __init__(self, APISERVER, DEPLOYMENT):
        self.apiServer = APISERVER
        self.deployment = DEPLOYMENT
        self.internalQueue = []

    def UpdatePodList(self):
        self.internalQueue.clear()
        endPoints = self.apiServer.GetEndPointsByLabel(self.deployment.deploymentLabel)
        for endPoint in endPoints:
            if endPoint.pod and endPoint.pod.isRunning():
                queueItem = LoadBalancerQueue(endPoint.pod, len(endPoint.pod.requests))
                self.internalQueue.append(queueItem)

    def FindPriorityQueueItem(self):
        priorityQueueItem = self.internalQueue[0]
        for queueItem in self.internalQueue:
            if queueItem.priority < priorityQueueItem.priority:
                priorityQueueItem = queueItem
        return priorityQueueItem

    def FindPod(self):
        self.UpdatePodList()
        if len(self.internalQueue) > 0:
            queueItem = self.FindPriorityQueueItem()
            if queueItem is not None:
                return queueItem.pod
        return None