from src.api_server import APIServer
import time

#LoadBalancer distributes requests to pods in Deployments

class LoadBalancer:
	def __init__(self, APISERVER, DEPLOYMENT):
		self.apiServer = APISERVER
		self.deployment = DEPLOYMENT
		self.running = True
	
	def __call__(self):
		print("LoadBalancer start")
		while self.running:
			self.deployment.waiting.wait()
			with self.deployment.lock:
				requests = self.deployment.pendingReqs.copy()
				self.deployment.pendingReqs.clear()
			for request in requests:
				endPoints = self.apiServer.GetEndPointsByLabel(request.deploymentLabel)
				if len(endPoints)>0:
					pod = self.FindFirstAvailablePod(endPoints)
					pod.HandleRequest(request)
				else:
					print("No pod available to handle Request_"+request.label)
			self.deployment.waiting.clear()
		print("ReqHandlerShutdown")


	def FindFirstAvailablePod(self, endPoints):
		pod = endPoints[0].pod
		for endPoint in endPoints:
			if endPoint.pod.available_cpu > 0:
				pod = endPoint.pod
				break
		return pod