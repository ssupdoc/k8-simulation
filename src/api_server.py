from deployment import Deployment
from end_point import EndPoint
from etcd import Etcd
from pod import Pod
from worker_node import WorkerNode
from request import Request
import threading

# The APIServer handles the communication between controllers and the cluster. It houses
# the methods that can be called for cluster management


class APIServer:
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Lock()
		self.kubeletList = []
		self.requestWaiting = threading.Event()

# 	GetDeployments method returns the list of deployments stored in etcd
	def GetDeployments(self):
		return self.etcd.deploymentList

#	GetDeploymentByLabel method returns a deployment queried by deploymentLabel	
	def GetDeploymentByLabel(self, label):
		deployment_list = self.GetDeployments()
		return next(filter(lambda deployment: deployment.deploymentLabel == label, deployment_list), None)
		

#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.nodeList

#	GetPendingPodList method returns the list of PendingPods stored in etcd
	def GetPendingPodList(self):
		return self.etcd.pendingPodList

	def GetRunningPodList(self):
		return self.etcd.runningPodList

#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints(self):
		return self.etcd.endPointList

	def PrintEtcdWorkerList(self, label):
		worker_list = self.GetWorkers()
		print(label)
		for worker in worker_list:
			print(worker.__dict__)

# CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd nodeList
	def CreateWorker(self, info):
		print("\n\n\n")
		self.PrintEtcdWorkerList("ETCD worker list before")
		worker = WorkerNode(info)
		cur_worker_list = self.GetWorkers()
		cur_worker_list.append(worker)
		self.PrintEtcdWorkerList("ETCD worker list after")
		print("\n\n\n")

	def PrintEtcdDeploymentList(self, label):
		deployment_list = self.GetDeployments()
		print(label)
		for deployment in deployment_list:
			print(deployment.__dict__)


# CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(self, info):
		self.PrintEtcdDeploymentList("ETCD deployment list before")
		deployment = Deployment(info)
		cur_deployment_list = self.GetDeployments()
		cur_deployment_list.append(deployment)
		self.PrintEtcdDeploymentList("ETCD deployment list after")

# RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, deploymentLabel):
		deployment = self.GetDeploymentByLabel(deploymentLabel)
		deployment.expectedReplicas = 0

		end_point_list = self.GetEndPointsByLabel(deploymentLabel)
		for end_point in end_point_list:
			self.TerminatePod(end_point)

		self.etcd.pendingPodList = list(filter(lambda pod: pod.deploymentLabel != deploymentLabel, self.etcd.pendingPodList))


# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it
# to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):
		end_point = EndPoint(pod, worker)
		cur_end_point_list = self.GetEndPoints()
		cur_end_point_list.append(end_point)

# RemoveEndPoint removes end point from end point list
	def RemoveEndPoint(self, end_point):
		self.etcd.endPointList.remove(end_point)

# CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):
		return endPoint.pod and endPoint.pod.IsRunning()

# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):
		cur_end_point_list = self.GetEndPoints()
		deployment_end_points = list(filter(lambda end_point: end_point.deploymentLabel == deploymentLabel, cur_end_point_list))
		return deployment_end_points


# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deploymentLabel):
		deployment = self.GetDeploymentByLabel(deploymentLabel)
		if deployment is not None:
			podName = deploymentLabel + '-pod-' + str(deployment.currentReplicas + 1)
			pod = Pod(podName, deployment.cpuCost, deploymentLabel)
			self.etcd.pendingPodList.append(pod)
		

# GetPod returns the pod object
	def GetPod(self, endPoint):
		return endPoint.pod

# TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
# No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
# it will be deleted by the Kubelet
	def TerminatePod(self, end_point):
			end_point.pod.SetStatus("TERMINATING")

# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, depLabel):
		end_point_list = self.GetEndPointsByLabel(depLabel)
		end_point = next(filter(lambda end_point: end_point.pod.IsRunning(), end_point_list), None)
		if end_point:
			print("Crashing pod " + end_point.pod.podName)
			end_point.pod.crash.set()
			end_point.pod.SetStatus("FAILED")

# MoveToPending moves pod to pending
	def MoveToPending(self, pod):
		self.etcd.runningPodList.remove(pod)
		self.etcd.pendingPodList.append(pod)

# CheckPod finds if a pod has the req cpu cost
	def CheckPod(self, pod, cpuCost):
		return pod.assigned_cpu >= cpuCost

# FindPodsFromPending returns pods in a pending list that can accomodate a certain CPU cost
	def FindPodsFromPending(self, cpuCost):
		cur_pending_list = self.GetPendingPodList()
		return list(filter(lambda pod: pod.status == "PENDING" and pod.assigned_cpu >= cpuCost, cur_pending_list))

# AssignNode takes a pod in the pendingPodList and transfers it to the runningPodList
	def AssignNode(self, pod, worker):
		self.etcd.pendingPodList.remove(pod)
		self.etcd.runningPodList.append(pod)
		worker.AllocateCpu(pod.assigned_cpu)
		pod.SetStatus("RUNNING")

#	pushReq adds the incoming request to the handling queue
	def PushReq(self, info):
		self.etcd.reqCreator.submit(self.ReqHandle, info)


# Creates requests and notifies the handler of request to be dealt with

	def ReqHandle(self, info):
		self.etcd.pendingReqs.append(Request(info))
		self.requestWaiting.set()
	
	def DiscardRequest(self, req):
		print("\n~~~Discarding " + req.status + " request " + req.label + "(" + req.deploymentLabel + ")~~~\n")
		self.etcd.pendingReqs.remove(req)

# GetPendingRequests returns pending requests
	def GetPendingRequests(self):
		return self.etcd.pendingReqs