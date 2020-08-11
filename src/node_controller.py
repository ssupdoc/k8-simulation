from api_server import APIServer
import threading
import time


#NodeController is a control loop that monitors the status of WorkerNode objects in the cluster and ensures that the EndPoint objects stored in etcd are up to date.
#The NodeController will remove stale EndPoints and update to show changes in others
class NodeController:
	
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("NodeController start")
		while self.running:
			with self.apiServer.etcdLock:
				end_point_list = self.apiServer.GetEndPoints()
				obsolete_end_point = next(filter(lambda end_point: end_point.pod.IsDown(), end_point_list), None)
				if obsolete_end_point:
					pod = obsolete_end_point.pod

					node = obsolete_end_point.node
					node.deallocateCpu(pod.assigned_cpu)

					if pod.IsFailed():
						self.apiServer.MoveToPending(pod)
						pod.Refresh()

					self.apiServer.RemoveEndPoint(obsolete_end_point)

			time.sleep(self.time)

		print("NodeContShutdown")
