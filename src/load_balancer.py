from src.api_server import APIServer
from src.round_robin_load_balancer import RoundRobinLoadBalancer
from src.utilisation_aware_load_balancer import UtilisationAwareLoadBalancer
import time

#LoadBalancer distributes requests to pods in Deployments

class LoadBalancer:
	def __init__(self, APISERVER, DEPLOYMENT, TYPE):
		self.apiServer = APISERVER
		self.deployment = DEPLOYMENT
		self.running = True

		if TYPE == 'round_robin':
			self.balancer = RoundRobinLoadBalancer(APISERVER, DEPLOYMENT)
		elif TYPE == 'utilisation_aware':
			self.balancer = UtilisationAwareLoadBalancer(APISERVER, DEPLOYMENT)
	
	def __call__(self):
		print(f"LoadBalancer start -{self.deployment.deploymentLabel}")
		while self.running:
			self.deployment.waiting.wait()
			with self.deployment.lock:
				requests = self.deployment.pendingReqs.copy()
				self.deployment.pendingReqs.clear()
			for request in requests:
				pod = self.balancer.FindPod()
				if pod is not None:
					self.balancer.AssignPod(request, pod)
				else:
					print("No pod available to handle Request_"+request.label)
			self.deployment.waiting.clear()
		print(f"LoadBalanceShutdown -{self.deployment.deploymentLabel}")