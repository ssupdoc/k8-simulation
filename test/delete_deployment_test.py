from src.api_server import APIServer
import threading
from src.dep_controller import DepController
from src.scheduler import Scheduler
from src.node_controller import NodeController
import unittest
import time

apiServer = APIServer()
_depCtlLoop = 2
depController = DepController(apiServer, _depCtlLoop)
depControllerThread = threading.Thread(target=depController)
depControllerThread.start()
_scheduleCtlLoop =2
scheduler = Scheduler(apiServer, _scheduleCtlLoop)
schedulerThread = threading.Thread(target = scheduler)
schedulerThread.start()
_nodeCtlLoop = 2
nodeController = NodeController(apiServer, _nodeCtlLoop)
nodeControllerThread = threading.Thread(target=nodeController)
nodeControllerThread.start()

instructions = open("tracefiles/delete_deployment.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	# print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			apiServer.RemoveDeployment(cmdAttributes[1:])
		time.sleep(3)

time.sleep(5)

depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()

class TestEndPoints(unittest.TestCase):
	def test_end_point_length(self):
		self.assertEqual(len(apiServer.GetEndPointsByLabel('Deployment_AA')), 0)

class TestPods(unittest.TestCase):
	def test_pod_length(self):
		self.assertEqual(len(apiServer.GetPending()), 0)
		self.assertEqual(len(apiServer.etcd.runningPodList), 0)

class TestWorkers(unittest.TestCase):
    def test_node_cpus(self):
        worker = apiServer.etcd.nodeList[0]
        self.assertEqual(worker.available_cpu, worker.assigned_cpu)

class TestDeployments(unittest.TestCase):
	def test_deployment_list_length(self):
		self.assertEqual(len(apiServer.etcd.deploymentList), 0)
