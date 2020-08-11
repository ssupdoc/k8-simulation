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
		self.available_cpu = int(ASSIGNED_CPU)
		self.assigned_cpu = int(ASSIGNED_CPU)
		self.deploymentLabel = DEPLABEL
		self.status = "PENDING"
		self.crash = threading.Event()
		self.pool = ThreadPoolExecutor(max_workers=ASSIGNED_CPU)

	def HandleRequest(self, EXECTIME):
		self.available_cpu-=1
		handling = self.pool.submit(self.crash.wait(timeout=EXECTIME))
		self.available_cpu+=1
		if self.crash.isSet():
			self.SetStatus("FAILED")
		print('\n\n\n###Pod after handling req starts####')
		print('pod: ', self.podName)
		print('available CPU: ', self.available_cpu)
		print('status: ', self.status)
		print('Crash: ', handling._state)
		print('Actual crash: ',self.crash.isSet())
		print('###Pod after handling req ends###\n\n\n')


		# if handling._state is not "FINISHED": #Crash
		# 	self.SetStatus("FAILED")
		
	def SetStatus(self, status):
		self.status = status

	def IsRunning(self):
		return self.status == 'RUNNING'
	
	def IsTerminating(self):
		return self.status == "TERMINATING"

	def IsFailed(self):
		return self.status == "FAILED"

	def HasAvailableCPU(self):
		return self.available_cpu > 0

	def Refresh(self):
		self.SetStatus("PENDING")
		self.available_cpu = self.assigned_cpu
		self.crash.clear()
		self.pool = ThreadPoolExecutor(max_workers=self.assigned_cpu)