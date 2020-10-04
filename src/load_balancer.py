from src.api_server import APIServer
import time

#LoadBalancer distributes requests to pods in Deployments

class LoadBalancer:
	def __init__(self, KIND, APISERVER, DEPLOYMENT):
		self.apiServer = APISERVER
		self.deployment = DEPLOYMENT
		self.running = True
		self.kind = KIND
		self.index = 0
	
	def __call__(self):
		print("LoadBalancer start")
		while self.running:
			self.deployment.waiting.wait()
			#print(self.deployment.deploymentLabel+" LB Engaged")
			with self.deployment.lock:
				requests = self.deployment.pendingReqs.copy()
				#print(self.deployment.deploymentLabel+" requests: "+str(len(requests)))
				self.deployment.pendingReqs.clear()
				self.deployment.waiting.clear()
			with self.apiServer.etcdLock:
				endPoints = self.apiServer.GetEndPointsByLabel(self.deployment.deploymentLabel)
				if len(endPoints) == 0:
					print('no endpoints found for '+self.deployment.deploymentLabel)
					continue
				for request in requests:
					#Round Robin load balancer
					if self.kind == 'RR':
						if self.index >= len(endPoints):
							self.index = 0
						pod = self.apiServer.GetPod(endPoints[self.index])
						#print(pod.podName)
						pod.HandleRequest(request)
						self.index+=1
					#Utilization Aware load balancer
					elif self.kind == 'UA':
						endPoints.sort(key=lambda x: x.pod.available_cpu, reverse=True)
						pod = self.apiServer.GetPod(endPoints[0])
						pod.HandleRequest(request)

			
		print("LoadBalancer Shutdown")
