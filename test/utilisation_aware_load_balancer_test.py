from src.api_server import APIServer
from src.load_balancer import LoadBalancer
from src.abstract_load_balancer import LoadBalancerQueue
import unittest

LOADBALANCERTYPE = 'utilisation_aware'
DEPLOYMENT_INFO = ['Deployment_AA', 3, 2]

apiServer = APIServer()
apiServer.CreateDeployment(DEPLOYMENT_INFO)
deployment = apiServer.etcd.deploymentList[0]
loadBalancer = LoadBalancer(apiServer, deployment, LOADBALANCERTYPE)
loadBalancer.balancer.internalQueue = [ LoadBalancerQueue('test_pod_1', 5), LoadBalancerQueue('test_pod_2', 3) ]


class TestPriority(unittest.TestCase):
	def test_priority_pod(self):
		priorityItem = loadBalancer.balancer.FindPriorityQueueItem()
		self.assertEqual(priorityItem.pod, 'test_pod_2')
