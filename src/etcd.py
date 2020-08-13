from pod import Pod
from deployment import Deployment
from end_point import EndPoint
from worker_node import WorkerNode
from concurrent.futures import ThreadPoolExecutor
import threading

#Etcd is the storage component of the cluster that allows for comparison between expected
#configuration and real time information.
#pending_pod_list is a list of Pod objects that have been created by the Deployment Controller but have yet to
#be scheduled.
#deployment_list is a list of Deployment Objects.
#node_list is a list of the nodes within the cluster. in this assignment this consists only of WorkerNodes.
#end_point_list is a list of EndPoint objects.
class Etcd:
	def __init__(self):
		self.pending_pod_list = []
		self.running_pod_list= []
		self.deployment_list = []
		self.node_list = []
		self.end_point_list = []
		self.pending_reqs = []
		self.req_creator = ThreadPoolExecutor(max_workers=1)

