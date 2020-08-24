from api_server import APIServer
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
				requests = self.deployment.pendingReqs.copy
				self.deployment.pendingReqs.clear
			for request in self.requests:
				pass

			self.deployment.waiting.clear()
		print("ReqHandlerShutdown")