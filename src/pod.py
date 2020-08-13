import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading

#The Pod is the unit of scaling within Kubernetes. It encapsulates the running containerized application
#name is the name of the Pod. This is the deploymentLabel with the replica number as a suffix. ie "deploymentA1"
#assigned_cpu is the cost in cpu of deploying a Pod onto a Node
#available_cpu is how many cpu threads are currently available
#deploymentLabel is the label of the Deployment that the Pod is managed by
#status is a string that communicates the Pod's availability. ['PENDING','RUNNING', 'TERMINATING', 'FAILED']
#the pool is the threads that are available for request handling on the pod
class Pod:
	def __init__(self, NAME, ASSIGNED_CPU, DEPLABEL):
		self.podName = NAME
		self.available_cpu = 0
		self.assigned_cpu = int(ASSIGNED_CPU)
		self.deploymentLabel = DEPLABEL
		self.status = "PENDING"
		self.crash = threading.Event()
		self.pool = ThreadPoolExecutor(max_workers=ASSIGNED_CPU)

	def HandleRequest(self, req):
		if self.available_cpu > 0:
			self.available_cpu-=1
			print(f"\n\n***Request {req.label} is handled by {self.podName}***")
			print(f"Pod details: Status - {self.status} Assigned - {self.assigned_cpu} Available - {self.available_cpu}")
			self.pool.submit(self.crash.wait(timeout=req.execTime))
			self.available_cpu+=1
			if self.crash.isSet():
				self.SetStatus("FAILED")
				print(f"\n\n!!!Request {req.label} Failed by {self.podName} as it crashed!!!")
			else:
				print(f"\n\n***Request {req.label} Completed by {self.podName}***")
			print(f"Pod details: Status - {self.status} Assigned - {self.assigned_cpu} Available - {self.available_cpu}")
		else:
			print(f"!!!Pod {self.podName} cannot handle request {req.label} due to non-availability of CPUs!!!")
		
	def SetStatus(self, status):
		self.status = status

	def IsRunning(self):
		return self.status == 'RUNNING'
	
	def IsTerminating(self):
		return self.status == "TERMINATING"

	def IsFailed(self):
		return self.status == "FAILED"
	
	def IsDown(self):
		return (self.status == 'TERMINATING') or (self.status == 'FAILED')

	def HasAvailableCPU(self):
		return self.available_cpu > 0

	def IsIdle(self):
		return self.available_cpu == self.assigned_cpu

	def Refresh(self):
		self.SetStatus("PENDING")
		self.available_cpu = 0
		self.crash.clear()
	
	def Run(self):
		self.available_cpu = self.assigned_cpu
		self.SetStatus("RUNNING")