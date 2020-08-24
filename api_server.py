from deployment import Deployment
from end_point import EndPoint
from etcd import Etcd
from pod import Pod
from MyController import PIDController
from request import Request
from worker_node import WorkerNode
import threading
import random

#The APIServer handles the communication between controllers and the cluster. It houses
#the methods that can be called for cluster management

class APIServer:
	def __init__(self):
		self.etcd = Etcd()
		self.etcdLock = threading.Lock()
		self.kubeletList = [] 
		self.requestWaiting = threading.Event()
		self.controller = PIDController(0,0,0)#Tune your controller
	
# 	GetDeployments method returns the list of deployments stored in etcd 	
	def GetDeployments(self):
		return self.etcd.deploymentList.copy()
		
#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.nodeList.copy()
		
#	GetPending method returns the list of PendingPods stored in etcd
	def GetPending(self):
		return self.etcd.pendingPodList.copy()
		
#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints(self):
		return self.etcd.endPointList.copy()
		
# CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd nodeList
	def CreateWorker(self, info):
		worker = WorkerNode(info)
		self.etcd.nodeList.append(worker)
		print("Worker_Node " + worker.label + " created")
		
# CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deploymentList
	def CreateDeployment(self, info):
		deployment = Deployment(info)
		self.etcd.deploymentList.append(deployment)
		print("Deployment " + deployment.deploymentLabel + " created")
		
# RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, info):
		for deployment in self.etcd.deploymentList:
			if deployment.deploymentLabel == info[0]:
				deployment.expectedReplicas = 0
				
# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it 
# to the endPointList in etcd
	def CreateEndPoint(self, pod, worker):
		endPoint = EndPoint(pod, pod.deploymentLabel, worker)
		self.etcd.endPointList.append(endPoint)
		print("New Endpoint for "+endPoint.deploymentLabel+"- NODE: "+ endPoint.node.label + " POD: " + endPoint.pod.podName)


# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deploymentLabel):
		endPoints = []
		for endPoint in self.etcd.endPointList:
			if endPoint.deploymentLabel == deploymentLabel:
				endPoints.append(endPoint)
		return endPoints

#RemoveEndPoint removes the EndPoint from the list within etcd
	def RemoveEndPoint(self, endPoint):
		endPoint.node.available_cpu+=endPoint.pod.assigned_cpu
		print("Removing EndPoint for: "+endPoint.deploymentLabel)
		self.etcd.endPointList.remove(endPoint)

#GeneratePodName creates a random label for a pod
	def GeneratePodName(self):
		label = random.randint(111,999)
		for pod in self.etcd.runningPodList:
			if pod.podName == label:
				label = self.GeneratePodName()
		for pod in self.etcd.pendingPodList:
			if pod.podName == label:
				label = self.GeneratePodName()
		return label


# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deployment):
		podName = deployment.deploymentLabel + "_" + str(self.GeneratePodName())
		pod = Pod(podName, deployment.cpuCost, deployment.deploymentLabel)
		print("Pod " + pod.podName + " created")
		self.etcd.pendingPodList.append(pod)
		
# GetPod returns the pod object associated with an EndPoint
	def GetPod(self, endPoint):
		return endPoint.pod

#TerminatePod gracefully shuts down a Pod
	def TerminatePod(self, endPoint):
		pod = endPoint.pod
		pod.status="TERMINATING"
		self.RemoveEndPoint(endPoint)
		print("Removing Pod "+pod.podName)


# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, info):
		endPoints = self.GetEndPointsByLabel(info[0])
		if len(endPoints) == 0:
			print("No Pods to crash")
		else:
			print("GETTING PODS")
			pod = self.GetPod(endPoints[0])
			pod.status = "FAILED"
			pod.crash.set()
			print ("Pod "+pod.podName+" crashed")

#	Alter these method so that the requests are pushed to Deployments instead of etcd
	def PushReq(self, info):
		self.etcd.reqCreator.submit(self.ReqPusher, info)


	def ReqPusher(self, info):
		self.etcd.pendingReqs.append(Request(info))
		self.requestWaiting.set()
