from src.api_server import APIServer
from src.load_balancer import LoadBalancer
from src.hpa import HPA
from src.pod import Pod
import unittest

LOADBALANCERTYPE = 'utilisation_aware'
DEPLOYMENT_INFO = ['Deployment_AA', 2, 2]
HPA_INFO = ['Deployment_AA', 75, 10, 5]
_hpaCtlLoop = 2

apiServer = APIServer()
apiServer.CreateDeployment(DEPLOYMENT_INFO)
deployment = apiServer.etcd.deploymentList[0]

podName = deployment.deploymentLabel + "_" + str(apiServer.GeneratePodName())
pod = Pod(podName, deployment.cpuCost, deployment.deploymentLabel)
pod.status = "RUNNING"
pod.requests = [ 'Req 1' ]
pod.available_cpu -= 1

podList = [pod, pod]

hpa = HPA(apiServer, _hpaCtlLoop, HPA_INFO)


class TestUtilisation(unittest.TestCase):
	def test_average_utilisation(self):
		load = hpa.calculateAvgUtil(deployment, podList)
		self.assertEqual(load, 0.5)

class TestController(unittest.TestCase):
	def test_controller_update(self):
		hpa.updateController(10, 12)
		self.assertEqual(hpa.controller.kp, 10)
		self.assertEqual(hpa.controller.ki, 12)
		self.assertEqual(hpa.pValue, 10)
		self.assertEqual(hpa.iValue, 12)
