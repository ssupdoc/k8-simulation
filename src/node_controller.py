from api_server import APIServer
import threading
import time


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController:
	
	def __init__(self, api_server, LOOPTIME):
		self.api_server = api_server
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("NodeController start")
		while self.running:
			with self.api_server.etcd_lock:
				end_point_list = self.api_server.GetEndPoints()
				obsolete_end_point = next(filter(lambda end_point: end_point.pod.IsDown(), end_point_list), None)
				if obsolete_end_point:
					pod = obsolete_end_point.pod
					self.api_server.DeallocateCPUFromWorker(obsolete_end_point.node, pod.assigned_cpu)
					if pod.IsFailed():
						self.api_server.MoveToPending(pod)
						pod.Refresh()
					self.api_server.RemoveEndPoint(obsolete_end_point)
			time.sleep(self.time)
		print("NodeContShutdown")
