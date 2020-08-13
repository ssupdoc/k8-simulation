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
					if deployment.expectedReplicas == 0:
						end_point_list = self.apiServer.GetEndPointsByLabel(deployment.deploymentLabel)
						for end_point in end_point_list:
							pod = end_point.pod
							running_pod_list = self.apiServer.GetRunningPodList()
							if pod in running_pod_list and pod.IsIdle():
								print("\n\n!!!Deleting Pod " + pod.podName + " !!!")
								running_pod_list.remove(pod)
								deployment.RemoveReplicas(1)
								self.CleanupDeploymentList(deployment, running_pod_list, cur_deployment_list)
					while deployment.expectedReplicas and deployment.currentReplicas < deployment.expectedReplicas:
						self.apiServer.CreatePod(deployment.deploymentLabel)
						deployment.currentReplicas += 1

			time.sleep(self.time)
		print("DepContShutdown")

	def CleanupDeploymentList(self, deployment, running_pod_list, deployment_list):
		does_pod_exist_for_deployment  = any(pod.deploymentLabel == deployment.deploymentLabel for pod in running_pod_list)
		print(f"\n\n!!!Cleaning up deployment {deployment.deploymentLabel}: Pods exist - {does_pod_exist_for_deployment}!!!")
		if not does_pod_exist_for_deployment:
			deployment_list.remove(deployment)
			print(f"!!!Deployment {deployment.deploymentLabel} deleted!!!")
		else:
			print(f"XXXUnable to delete deployment {deployment.deploymentLabel}XXX")