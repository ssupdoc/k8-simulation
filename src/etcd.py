from src.pod import Pod
from src.deployment import Deployment
from src.end_point import EndPoint
from src.worker_node import WorkerNode
from concurrent.futures import ThreadPoolExecutor
import threading

#Etcd is the storage component of the cluster that allows for comparison between expected
#configuration and real time information.
#pendingPodList is a list of Pod objects that have been created by the Deployment Controller but have yet to
#be scheduled.
#runningPodList is the list of scheduled Pods
#deploymentList is a list of Deployment Objects.
#nodeList is a list of the nodes within the cluster. in this assignment this consists only of WorkerNodes.
#endPointList is a list of EndPoint objects.
#pendingReqs is the queue of incoming requests to be handled
#reqCreator is the thread that takes in requests
class Etcd:
	def __init__(self):
		self.pendingPodList = []
		self.runningPodList= []
		self.deploymentList = []
		self.nodeList = []
		self.endPointList = []
		self.pendingReqs = []
		self.reqCreator = ThreadPoolExecutor(max_workers=1)

