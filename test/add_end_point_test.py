from src.api_server import APIServer
import threading
from src.dep_controller import DepController
from src.scheduler import Scheduler
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
scheduler.running = False
apiServer.requestWaiting.set()
depControllerThread.join()
schedulerThread.join()

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
