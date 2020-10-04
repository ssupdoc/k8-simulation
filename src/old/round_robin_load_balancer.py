from src.abstract_load_balancer import AbstractLoadBalancer, LoadBalancerQueue


class RoundRobinLoadBalancer(AbstractLoadBalancer):
    def __init__(self, APISERVER, DEPLOYMENT):
        self.apiServer = APISERVER
        self.deployment = DEPLOYMENT
        self.internalQueue = []

    def UpdatePodList(self):
        endPoints = self.apiServer.GetEndPointsByLabel(self.deployment.deploymentLabel)
        for endPoint in endPoints:
            pods_in_queue = list(map(lambda queue_item: queue_item.pod, self.internalQueue))
            if endPoint.pod not in pods_in_queue and endPoint.pod.isRunning():
                queueItem = LoadBalancerQueue(endPoint.pod, self.FindLeastPriorityInQueue() + 1)
                self.internalQueue.append(queueItem)

    def FindPriorityQueueItem(self): 
        priorityQueueItem = None
        for queueItem in self.internalQueue:
            if queueItem.pod.isRunning():
                if priorityQueueItem is None:
                    priorityQueueItem = queueItem
                elif queueItem.priority < priorityQueueItem.priority:
                    priorityQueueItem = queueItem
        return priorityQueueItem

    def FindPod(self):
        self.UpdatePodList()
        if len(self.internalQueue) > 0:
            queueItem = self.FindPriorityQueueItem()
            if queueItem is not None:
                self.RotatePriority(queueItem)
                return queueItem.pod
        return None
    
    def FindLeastPriorityInQueue(self):
        if len(self.internalQueue):
            leastPriorityItem = self.internalQueue[0]
            for queueItem in self.internalQueue:
                if queueItem.priority > leastPriorityItem.priority:
                    leastPriorityItem = queueItem
            return leastPriorityItem.priority
        else: 
            return 0

    def RotatePriority(self, queueItem):
        queueItem.priority = self.FindLeastPriorityInQueue() + 1