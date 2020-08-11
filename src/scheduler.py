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
			with self.apiServer.etcdLock:
				pending_pod_list = self.apiServer.GetPendingPodList()
				worker_list = self.apiServer.GetWorkers()
				suitable_worker_node = None
				pod = None
				for pending_pod in pending_pod_list:
					suitable_worker_node = next(filter(lambda node: node.available_cpu >= pending_pod.assigned_cpu, worker_list), None)
					if suitable_worker_node is not None:
						pod = pending_pod
						break
				if pod is not None and suitable_worker_node is not None:
					print("\n\n\n~~~Creating endpoint starts~~~")
					print("End point creation: ", pod.podName, pod.deploymentLabel, suitable_worker_node.label)
					self.apiServer.CreateEndPoint(pod, suitable_worker_node)
					print("~~~Creating endpoint ends~~~\n\n\n")
					self.apiServer.AssignNode(pod, suitable_worker_node)			
			time.sleep(self.time)

		print("SchedShutdown")
