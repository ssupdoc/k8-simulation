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

class TestEndPoints(unittest.TestCase):
	def test_end_point_length(self):
		self.assertEqual(len(apiServer.GetEndPointsByLabel('Deployment_AA')), 2)

class TestPods(unittest.TestCase):
	def test_pod_length(self):
		self.assertEqual(len(apiServer.GetPending()), 0)
		self.assertEqual(len(apiServer.etcd.runningPodList), 2)

class TestWorkers(unittest.TestCase):
    def test_node_cpus(self):
        worker = apiServer.etcd.nodeList[0]
        self.assertEqual(worker.available_cpu, 0)
