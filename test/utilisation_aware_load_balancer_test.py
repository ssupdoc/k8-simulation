from src.api_server import APIServer
from src.load_balancer import LoadBalancer
from src.abstract_load_balancer import LoadBalancerQueue
from src.constants import LoadBalancerType
import unittest

LOADBALANCERTYPE = LoadBalancerType.UTILISATION_AWARE
DEPLOYMENT_INFO = ['Deployment_AA', 3, 2]

apiServer = APIServer()
apiServer.CreateDeployment(DEPLOYMENT_INFO)
deployment = apiServer.etcd.deploymentList[0]
apiServer.CreatePod(deployment)
apiServer.CreatePod(deployment)
podList = apiServer.GetPending()
for pod in podList:
	pod.status = "RUNNING"
loadBalancer = LoadBalancer(apiServer, deployment, LOADBALANCERTYPE)
loadBalancer.balancer.internalQueue = [ LoadBalancerQueue(podList[0], 5), LoadBalancerQueue(podList[1], 3) ]


class TestPriority(unittest.TestCase):
	def test_priority_pod(self):
		priorityItem = loadBalancer.balancer.FindPriorityQueueItem()
		self.assertEqual(priorityItem.pod.podName, podList[1].podName)
