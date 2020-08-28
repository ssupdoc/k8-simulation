from src.api_server import APIServer
import threading
from src.dep_controller import DepController
from src.req_handler import ReqHandler
from src.node_controller import NodeController
from src.scheduler import Scheduler
from src.load_balancer import LoadBalancer
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

instructions = open("tracefiles/simple_request.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	# print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			loadbalancer = LoadBalancer(apiServer, deployment)
			lbThread = threading.Thread(target=loadbalancer)
			lbThread.start()
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			apiServer.RemoveDeployment(cmdAttributes[1:])
	if cmdAttributes[0] == 'Sleep':
		time.sleep(int(cmdAttributes[1]))
	time.sleep(3)
    

time.sleep(5)

print("Shutting down threads")

reqHandler.running = False
depController.running = False
scheduler.running = False
nodeController.running = False
loadbalancer.running = False
apiServer.requestWaiting.set()
loadbalancer.deployment.waiting.set()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
reqHandlerThread.join()
lbThread.join()

class TestPods(unittest.TestCase):
	def test_pod_cpu(self):
		pod = apiServer.etcd.runningPodList[0]
		self.assertEqual(pod.available_cpu, pod.assigned_cpu)
	def test_running_pods(self):
		self.assertEqual(len(apiServer.etcd.runningPodList), 1)
	def test_requests(self):
		pod = apiServer.etcd.runningPodList[0]
		self.assertEqual(len(pod.requests), 0)
