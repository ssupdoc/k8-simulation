from api_server import APIServer
import threading
import time

#The Scheduler is a control loop that checks for any pods that have been created
#but not yet deployed, found in the etcd pending_pod_list.
#It transfers Pod objects from the pending_pod_list to the running_pod_list and creates an EndPoint object to store in the etcd EndPoint list
#If no WorkerNode is available that can take the pod, it remains in the pending_pod_list
class Scheduler(threading.Thread):
	def __init__(self, api_server, LOOPTIME):
		self.api_server = api_server
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("Scheduler start")
		while self.running:
			with self.api_server.etcd_lock:
				pending_pod_list = []
				pending_pod_list[:] = self.api_server.GetPendingPodList()
				worker_list = self.api_server.GetWorkers()
				suitable_worker_node = None
				# Assign pending pods to suitable nodes and create an endpoint for the same
				for pending_pod in pending_pod_list:
					suitable_worker_node = next(filter(lambda node: node.available_cpu >= pending_pod.assigned_cpu, worker_list), None)
					if suitable_worker_node is not None:
						self.api_server.CreateEndPoint(pending_pod, suitable_worker_node)
						self.api_server.AssignNode(pending_pod, suitable_worker_node)
					else:
						print(f"\n\n^^^No worker available for {pending_pod.pod_name}. Scheduled for retrying^^^")		
			time.sleep(self.time)

		print("SchedShutdown")
