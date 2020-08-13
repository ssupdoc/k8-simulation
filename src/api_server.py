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
		self.etcd_lock = threading.Lock()
		self.request_waiting = threading.Event()

# 	GetDeployments method returns the list of deployments stored in etcd
	def GetDeployments(self):
		return self.etcd.deployment_list

#	GetDeploymentByLabel method returns a deployment queried by deployment_label	
	def GetDeploymentByLabel(self, label):
		deployment_list = self.GetDeployments()
		return next(filter(lambda deployment: deployment.deployment_label == label, deployment_list), None)

#	GetWorkers method returns the list of WorkerNodes stored in etcd
	def GetWorkers(self):
		return self.etcd.node_list

#	GetPendingPodList method returns the list of PendingPods stored in etcd
	def GetPendingPodList(self):
		return self.etcd.pending_pod_list

	def GetRunningPodList(self):
		return self.etcd.running_pod_list
	
	def RemoveRunningPod(self, pod):
		running_pod_list = self.GetRunningPodList()
		if pod in running_pod_list:
			running_pod_list.remove(pod)


#	GetEndPoints method returns the list of EndPoints stored in etcd
	def GetEndPoints(self):
		return self.etcd.end_point_list

	def PrintEtcdWorkerList(self, label):
		worker_list = self.GetWorkers()
		print(f"\n\n\n{label}")
		for worker in worker_list:
			print(worker.__dict__)

# CreateWorker creates a WorkerNode from a list of arguments and adds it to the etcd node_list
	def CreateWorker(self, info):
		worker = WorkerNode(info)
		cur_worker_list = self.GetWorkers()
		cur_worker_list.append(worker)
		self.PrintEtcdWorkerList("***Worker Nodes***")

	def DeallocateCPUFromWorker(self, worker, no_of_cpu):
		worker.deallocateCpu(no_of_cpu)

	def PrintEtcdDeploymentList(self, label):
		deployment_list = self.GetDeployments()
		print(f"\n\n\n{label}")
		for deployment in deployment_list:
			print(deployment.__dict__)


# CreateDeployment creates a Deployment object from a list of arguments and adds it to the etcd deployment_list
	def CreateDeployment(self, info):
		deployment = Deployment(info)
		cur_deployment_list = self.GetDeployments()
		cur_deployment_list.append(deployment)
		self.PrintEtcdDeploymentList("***Deployment list***")

	def AddReplicasToDeployment(self, deployment, replicas):
		deployment.AddReplicas(replicas)

# RemoveDeployment deletes the associated Deployment object from etcd and sets the status of all associated pods to 'TERMINATING'
	def RemoveDeployment(self, deployment_label):
		deployment = self.GetDeploymentByLabel(deployment_label)
		deployment.expected_replicas = 0
		end_point_list = self.GetEndPointsByLabel(deployment_label)
		for end_point in end_point_list:
			self.TerminatePod(end_point)
		self.RemoveFromPendingPodList(deployment)

	def RemoveFromPendingPodList(self, deployment):
		pending_pods_with_deployment = list(filter(lambda pod: pod.deployment_label == deployment.deployment_label, self.etcd.pending_pod_list))
		self.etcd.pending_pod_list = list(filter(lambda pod: pod.deployment_label != deployment.deployment_label, self.etcd.pending_pod_list))
		if pending_pods_with_deployment:
			self.RemoveReplicasFromDeployment(deployment, len(pending_pods_with_deployment))

	def RemoveReplicasFromDeployment(self, deployment, no_of_replicas):
		deployment.RemoveReplicas(no_of_replicas)

	def CleanupDeployment(self, deployment):
		deployment_list = self.GetDeployments()
		running_pod_list = self.GetRunningPodList()
		does_pod_exist_for_deployment  = any(pod.deployment_label == deployment.deployment_label for pod in running_pod_list)
		print(f"\n\n!!!Cleaning up deployment {deployment.deployment_label}: Pods exist - {does_pod_exist_for_deployment}!!!")
		if not does_pod_exist_for_deployment:
			deployment_list.remove(deployment)
			print(f"!!!Deployment {deployment.deployment_label} deleted!!!")
		else:
			print(f"XXXUnable to delete deployment {deployment.deployment_label}XXX")

# CreateEndpoint creates an EndPoint object using information from a provided Pod and Node and appends it
# to the end_point_list in etcd
	def CreateEndPoint(self, pod, worker):
		end_point = EndPoint(pod, worker)
		cur_end_point_list = self.GetEndPoints()
		cur_end_point_list.append(end_point)
		print(f"\n\n***End point created for {pod.podName} and {worker.label} for {pod.deployment_label}***")

# RemoveEndPoint removes end point from end point list
	def RemoveEndPoint(self, end_point):
		self.etcd.end_point_list.remove(end_point)
		print(f"\n\n!!!Endpoint removed between {end_point.pod.podName} and {end_point.node.label}")

# CheckEndPoint checks that the associated pod is still present on the expected WorkerNode
	def CheckEndPoint(self, endPoint):
		return endPoint.pod and endPoint.pod.IsRunning()

# GetEndPointsByLabel returns a list of EndPoints associated with a given deployment
	def GetEndPointsByLabel(self, deployment_label):
		cur_end_point_list = self.GetEndPoints()
		deployment_end_points = list(filter(lambda end_point: end_point.deployment_label == deployment_label, cur_end_point_list))
		return deployment_end_points


# CreatePod finds the resource allocations associated with a deployment and creates a pod using those metrics
	def CreatePod(self, deployment_label):
		deployment = self.GetDeploymentByLabel(deployment_label)
		if deployment is not None:
			podName = deployment_label + '-pod-' + str(deployment.current_replicas + 1)
			pod = Pod(podName, deployment.cpu_cost, deployment_label)
			self.etcd.pending_pod_list.append(pod)
		
# GetPod returns the pod object
	def GetPod(self, endPoint):
		return endPoint.pod

	def EngagePod(self, pod, req):
		if pod and req:
			pod.HandleRequest(req)

# TerminatePod finds the pod associated with a given EndPoint and sets it's status to 'TERMINATING'
# No new requests will be sent to a pod marked 'TERMINATING'. Once its current requests have been handled,
# it will be deleted by the Kubelet
	def TerminatePod(self, end_point):
			end_point.pod.SetStatus("TERMINATING")
			end_point.pod.pool.shutdown()
			print(f"\n\n!!!Pod {end_point.pod.podName} set to terminate!!!")

# CrashPod finds a pod from a given deployment and sets its status to 'FAILED'
# Any resource utilisation on the pod will be reset to the base 0
	def CrashPod(self, depLabel):
		end_point_list = self.GetEndPointsByLabel(depLabel)
		end_point = next(filter(lambda end_point: end_point.pod.IsRunning(), end_point_list), None)
		if end_point:
			print("\n\n!!!Crashing pod " + end_point.pod.podName + "!!!")
			end_point.pod.crash.set()
			end_point.pod.SetStatus("FAILED")

# MoveToPending moves pod to pending
	def MoveToPending(self, pod):
		self.etcd.running_pod_list.remove(pod)
		self.etcd.pending_pod_list.append(pod)

# CheckPod finds if a pod has the req cpu cost
	def CheckPod(self, pod, cpu_cost):
		return pod.assigned_cpu >= cpu_cost

# FindPodsFromPending returns pods in a pending list that can accomodate a certain CPU cost
	def FindPodsFromPending(self, cpu_cost):
		cur_pending_list = self.GetPendingPodList()
		return list(filter(lambda pod: pod.status == "PENDING" and pod.assigned_cpu >= cpu_cost, cur_pending_list))

	def GetRunningPodsByDeployment(self, deployment_label):
		running_pod_list = self.GetRunningPodList()
		return list(filter(lambda pod: pod.deployment_label == deployment_label, running_pod_list))

# AssignNode takes a pod in the pending_pod_list and transfers it to the running_pod_list
	def AssignNode(self, pod, worker):
		self.etcd.pending_pod_list.remove(pod)
		self.etcd.running_pod_list.append(pod)
		worker.AllocateCpu(pod.assigned_cpu)
		pod.Run()
		print(f"*** Pod {pod.podName} is running on worker node {worker.label}***")

#	AddReq adds the incoming request to the handling queue
	def AddReq(self, info):
		self.etcd.req_creator.submit(self.AppendReq, info)

# AppendReq Creates requests and notifies the handler of request to be dealt with
	def AppendReq(self, info):
		req = Request(info)
		print(f'\n\n***Request created label: {req.label}({req.exec_time}s) for deployment {req.deployment_label}')
		self.etcd.pending_reqs.append(req)
		self.request_waiting.set()
	
	def DiscardRequest(self, req, status):
		print("\n~~~Discarding " + status + " request " + req.label + "(" + req.deployment_label + ")~~~\n")
		self.etcd.pending_reqs.remove(req)

# GetPendingRequests returns pending requests
	def GetPendingRequests(self):
		return self.etcd.pending_reqs