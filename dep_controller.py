from api_server import APIServer
import threading
import time


#DepController is a control loop that creates and terminates Pod objects based on
#the expected number of replicas.
class DepController:
	def __init__(self, APISERVER, LOOPTIME):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("depController start")
		while self.running:
			deployments= []
			with self.apiServer.etcdLock:
				for deployment in self.apiServer.etcd.deploymentList:
					while deployment.currentReplicas < deployment.expectedReplicas:
						self.apiServer.CreatePod(deployment)
						deployment.currentReplicas +=1
					while deployment.currentReplicas > deployment.expectedReplicas:
						endPoints = self.apiServer.GetEndPointsByLabel(deployment.deploymentLabel)
						for endPoint in endPoints:
							self.apiServer.TerminatePod(endPoint)
							deployment.currentReplicas-=1
						for pod in self.apiServer.etcd.pendingPodList:
							if pod.deploymentLabel == deployment.deploymentLabel:
								self.apiServer.etcd.pendingPodList.remove(pod)
								deployment.currentReplicas-=1
					if deployment.expectedReplicas > 0:
						deployments.append(deployment)
				self.apiServer.etcd.deploymentList = deployments
			time.sleep(self.time)
		print("DepContShutdown")
