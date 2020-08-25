from src.api_server import APIServer
import threading
from src.dep_controller import DepController
import unittest
import time

apiServer = APIServer()
_depCtlLoop = 2
depController = DepController(apiServer, _depCtlLoop)
depControllerThread = threading.Thread(target=depController)
depControllerThread.start()

instructions = open("tracefiles/add_deployment.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	# print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])

time.sleep(5)

depController.running = False
apiServer.requestWaiting.set()
depControllerThread.join()

class TestAddDeployment(unittest.TestCase):
	def test_deployment_length(self):
		self.assertEqual(len(apiServer.GetDeployments()), 1)

	def test_deployment_data(self):
		deployment = apiServer.etcd.deploymentList[0]
		self.assertEqual(deployment.expectedReplicas, 2)
		self.assertEqual(deployment.cpuCost, 2)
		self.assertEqual(deployment.currentReplicas, 2)


class TestAddPods(unittest.TestCase):
	def test_pod_length(self):
		self.assertEqual(len(apiServer.GetPending()), 2)
