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

#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.nodeList

#	GetPending method returns the list of PendingPods stored in etcd
	def GetPending(self):
		return self.etcd.pendingPodList

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
		self.PrintEtcdWorkerList("ETCD worker list before")
		worker = WorkerNode(info)
		cur_worker_list = self.GetWorkers()
		cur_worker_list.append(worker)
		self.PrintEtcdWorkerList("ETCD worker list after")

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
		pass

# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it
# to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):
		pass

# CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):
		pass

# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):
		pass

# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deploymentLabel):
		pass

# GetPod returns the pod object stored in the internal podList of a WorkerNode
	def GetPod(self, endPoint):
		pass

# TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
# No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
# it will be deleted by the Kubelet
	def TerminatePod(self, endPoint):
		pass

# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, depLabel):
		pass

# AssignNode takes a pod in the pendingPodList and transfers it to the internal podList of a specified WorkerNode
	def AssignNode(self, pod, worker):
		pass

#	pushReq adds the incoming request to the handling queue
	def PushReq(self, info):
		self.etcd.reqCreator.submit(self.reqHandle, info)


# Creates requests and notifies the handler of request to be dealt with

	def reqHandle(self, info):
		self.etcd.pendingReqs.append(Request(info))
		self.requestWaiting.set()
