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
				deployment = self.apiServer.GetDepByLabel(request.deploymentLabel)
				deployment.pendingReqs.append(request)
				deployment.waiting.set()
				self.apiServer.requestWaiting.clear()
		print("ReqHandlerShutdown")