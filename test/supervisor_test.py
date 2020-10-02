from src.api_server import APIServer
from src.load_balancer import LoadBalancer
from src.hpa import HPA
from src.pod import Pod
import unittest
from src.supervisor import Supervisor

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

supervisor = Supervisor(apiServer, hpa)
supervisor.pValues =  [2.75,2.5,2.5,2.5,2.5,2.5,2.5,2.25,2.25,2.25,2,2,2,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75,1.75]
supervisor.iValues =  [5.3,5.3,5.3,5.3,5.4,5.6,5.5,5.5,5.5,5.6,5.7,5.9,6,5.9,5.8,6.1,6.2,6.1,6.1,6.1,5.9,6.2,6.2,6.1]
supervisor.avgErrors =  [1464,1394,1357,1293,1256,1254,1234,1195,1159,1167,1130,1075,1047,965,943,958,971,949,884,866,876,822,704,719]


class TestModel(unittest.TestCase):
    def test_regression_score(self):
        supervisor.performRegression()
        self.assertGreater(supervisor.scoreList[0], 0.8)

class TestConstrians(unittest.TestCase):
    def test_constraint_check(self):
        self.assertEqual(supervisor.checkConstraint(1,2,1,1, 0.1), False)
