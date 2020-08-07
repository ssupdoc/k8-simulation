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
			with self.apiServer.etcdLock:
				cur_deployment_list = self.apiServer.GetDeployments()
				for deployment in cur_deployment_list: # For each deployment check and add replicas if necessary
					while deployment.currentReplicas < deployment.expectedReplicas:
						self.apiServer.CreatePod(deployment.deploymentLabel)
						deployment.currentReplicas += 1

			time.sleep(self.time)
		print("DepContShutdown")
