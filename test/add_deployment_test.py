from src.api_server import APIServer
import threading
from src.dep_controller import DepController
from src.req_handler import ReqHandler
from src.node_controller import NodeController
from src.scheduler import Scheduler
import unittest
import time

_nodeCtlLoop = 2
_depCtlLoop = 2
_scheduleCtlLoop =2

apiServer = APIServer()
depController = DepController(apiServer, _depCtlLoop)
nodeController = NodeController(apiServer, _nodeCtlLoop)
reqHandler = ReqHandler(apiServer)
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
depControllerThread = threading.Thread(target=depController)
nodeControllerThread = threading.Thread(target=nodeController)
reqHandlerThread = threading.Thread(target=reqHandler)
schedulerThread = threading.Thread(target = scheduler)
print("Threads Starting")
reqHandlerThread.start()
nodeControllerThread.start()
depControllerThread.start()
schedulerThread.start()
print("ReadingFile")

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

print("Shutting down threads")

reqHandler.running = False
depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
reqHandlerThread.join()

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
		self.assertEqual(len(apiServer.etcd.runningPodList), 2)
