from deployment import Deployment
from end_point import EndPoint
from etcd import Etcd
from pod import Pod
from worker_node import WorkerNode
import threading

#The APIServer handles the communication between controllers and the cluster. It houses
#the methods that can be called for cluster management

class APIServer:
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Lock()
		self.kubeletList = [] 
		self.requestWaiting = threading.Event()
	
# 	GetDeployments method returns the list of deployments stored in etcd 	
	def GetDeployments():
		return etcd.deploymentList
		
#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers():
		return etcd.nodeList
		
#	GetPending method returns the list of PendingPods stored in etcd
	def GetPending():
		return etcd.pendingPodList
		
#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints():
		return etcd.endPointList
		
# CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd nodeList
	def CreateWorker(info):
	
# CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(info):
	
# RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(deploymentLabel):
	
# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it 
# to the endPointList in etcd
	def CreateEndPoint(pod, worker):
		    
# CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(endPoint):
	
# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(deploymentLabel):
	
# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(deploymentLabel):
	
# GetPod returns the pod object stored in the internal podList of a WorkerNode
	def GetPod(endPoint):
	
# TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
# No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
# it will be deleted by the Kubelet
	def TerminatePod(endPoint):
	
# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(depLabel):
	
# AssignNode takes a pod in the pendingPodList and transfers it to the internal podList of a specified WorkerNode
	def AssignNode(pod, worker):

#	pushReq adds the incoming request to the handling queue	
	def pushReq(info):	
	    etcd.reqCreator.submit(reqHandle, info)


#Creates requests and notifies the handler of request to be dealt with
	def reqHandle(info):
		etcd.pendingReqs.append(Request(info))
		self.requestWaiting.set()
