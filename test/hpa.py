from src.api_server import APIServer
from src.load_balancer import LoadBalancer
from src.hpa import HPA
from src.pod import Pod
import unittest

LOADBALANCERTYPE = 'utilisation_aware'
DEPLOYMENT_INFO = ['Deployment_AA', 3, 2]
HPA_INFO = ['Deployment_AA', 75, 10]
_hpaCtlLoop = 2

apiServer = APIServer()
apiServer.CreateDeployment(DEPLOYMENT_INFO)
deployment = apiServer.etcd.deploymentList[0]

podName = deployment.deploymentLabel + "_" + str(apiServer.GeneratePodName())
pod = Pod(podName, deployment.cpuCost, deployment.deploymentLabel)
pod.status = "RUNNING"
pod.requests = [ 'Req 1' ]

LOADMETRICS = [ 50, 60, 70]

hpa = HPA(apiServer, _hpaCtlLoop, HPA_INFO)


class TestLoad(unittest.TestCase):
	def test_pod_load_calculation(self):
		load = hpa.getLoadForPod(pod)
		self.assertEqual(load, 50)
	def test_average_load_calculation(self):
		averageLoad = hpa.getAverageLoad(LOADMETRICS)
		self.assertEqual(averageLoad, 60)
