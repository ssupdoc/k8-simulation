from api_server import APIServer
import threading
import time

#The Scheduler is a control loop that checks for any pods that have been created
#but not yet deployed, found in the etcd pendingPodList.
#It transfers Pod objects from the pendingPodList to the runningPodList and creates an EndPoint object to store in the etcd EndPoint list
#If no WorkerNode is available that can take the pod, it remains in the pendingPodList
class Scheduler(threading.Thread):
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("Scheduler start")
		while self.running:
			newPending = []
			with self.apiServer.etcdLock:
				for pod in self.apiServer.etcd.pendingPodList:
					for worker in self.apiServer.etcd.nodeList:
						if worker.status == "UP":
							if worker.available_cpu >= pod.assigned_cpu:
								pod.status = "RUNNING"
								print("Assigning Pod "+ pod.podName+" to Node "+worker.label)
								worker.available_cpu -= pod.assigned_cpu
								self.apiServer.CreateEndPoint(pod, worker)
								self.apiServer.etcd.runningPodList.append(pod)
								break
					if pod.status == "PENDING":
						newPending.append(pod)
				self.apiServer.etcd.pendingPodList = newPending
			time.sleep(self.time)
		print("SchedShutdown")
