from api_server import APIServer
import threading
import time


# DepController is a control loop that creates and terminates Pod objects based on
# the expected number of replicas.
class DepController:
	def __init__(self, api_server, LOOPTIME):
		self.api_server = api_server
		self.running = True
		self.time = LOOPTIME
	
	def __call__(self):
		print("depController start")
		while self.running:
			with self.api_server.etcd_lock:
				cur_deployment_list = self.api_server.GetDeployments()
				for deployment in cur_deployment_list:
					# If a deployment is set to be deleted, remove all idle pods and 
					# remove the deployment if all pods are deleted
					if deployment.expected_replicas == 0:
						deployment_pod_list = self.api_server.GetRunningPodsByDeployment(deployment.deployment_label)
						for pod in deployment_pod_list:
							if pod.IsIdle():
								print("\n\n!!!Deleting Pod " + pod.podName + " !!!")
								self.api_server.RemoveRunningPod(pod)
								self.api_server.RemoveReplicasFromDeployment(deployment, 1)
								self.api_server.CleanupDeployment(deployment)
					# Satisfy replica set point and add replicas AKA pods to the deployment
					# if necessary
					while deployment.expected_replicas and deployment.current_replicas < deployment.expected_replicas:
						self.api_server.CreatePod(deployment.deployment_label)
						self.api_server.AddReplicasToDeployment(deployment, 1)

			time.sleep(self.time)
		print("DepContShutdown")