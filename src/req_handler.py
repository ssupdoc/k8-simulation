from src.api_server import APIServer
import time

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler:
	def __init__(self, APISERVER):
		self.apiServer = APISERVER
		self.running = True
	
	def __call__(self):
		print("reqHandler start")
		while self.running:
			self.apiServer.requestWaiting.wait()
			with self.apiServer.etcdLock:
				requests =  self.apiServer.etcd.pendingReqs.copy()
				self.apiServer.etcd.pendingReqs.clear()
				self.apiServer.requestWaiting.clear()
			for request in requests:
				endPoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
				if len(endPoints)>0:
					pod = self.FindFirstAvailablePod(endPoints)
					pod.HandleRequest(request)
				else:
					print("No pod available to handle Request_"+request.label)
				self.apiServer.requestWaiting.clear()
		print("ReqHandlerShutdown")

	def FindFirstAvailablePod(self, endPoints):
		pod = endPoints[0].pod
		for endPoint in endPoints:
			if endPoint.pod.available_cpu > 0:
				pod = endPoint.pod
				break
		return pod