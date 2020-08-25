import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from src.request import Request
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
		self.assigned_cpu = int(ASSIGNED_CPU)
		self.available_cpu = int(ASSIGNED_CPU)
		self.deploymentLabel = DEPLABEL
		self.status = "PENDING"
		self.crash = threading.Event()
		self.pool = ThreadPoolExecutor(max_workers=ASSIGNED_CPU)

	def HandleRequest(self, REQUEST):
		def ThreadHandler():
			crashStatus = self.crash.wait(timeout=REQUEST.execTime)
			self.available_cpu += 1
			if crashStatus:
				print("Request_"+REQUEST.label+" failed")
			else: 
				print("Request_"+REQUEST.label+" Completed")
		self.available_cpu -= 1
		self.pool.submit(ThreadHandler)
		print("Request_"+REQUEST.label+" is handled by POD " + self.podName + " Remaining CPUs: " + str(self.available_cpu))
	
	