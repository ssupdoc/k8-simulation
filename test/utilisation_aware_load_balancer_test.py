import threading
from src.request import Request
from src.dep_controller import DepController
from src.api_server import APIServer
from src.req_handler import ReqHandler
from src.node_controller import NodeController
from src.scheduler import Scheduler
import matplotlib.pyplot as plt
import pandas as pd
from src.hpa import HPA
from src.load_balancer import LoadBalancer
from src.supervisor import Supervisor
import time
import unittest


#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 1
_depCtlLoop = 1
_scheduleCtlLoop =1
_hpaCtlLoop = 2

kind = 'UA'
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
#Simulation information
loadBalancers = []
loadBalancerThreads = []
SEED = "ua_loadbalancer"
instructions = open(f"tracefiles/{SEED}.txt", "r")
commands = instructions.readlines()

for command in commands:
	cmdAttributes = command.split()
	print(str(command))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			loadbalancer = LoadBalancer(kind, apiServer, deployment)
			lbThread = threading.Thread(target=loadbalancer)
			lbThread.start()
			loadBalancers.append(loadbalancer)
			loadBalancerThreads.append(lbThread)
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			#We have to makesure that our load balancer will end gracefully here
			for loadBalancer in loadBalancers:
				if loadBalancer.deployment.deploymentLabel == cmdAttributes[1]:
					loadBalancer.running=False
			apiServer.RemoveDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	#The instructions will sleep after each round of requests. The following code stores values for graphing
	if cmdAttributes[0] == 'Sleep':
		time.sleep(int(cmdAttributes[1]))
time.sleep(5)
print("Shutting down threads")
reqHandler.running = False
depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
for loadbalancer in loadBalancers:
	loadbalancer.running = False
	loadbalancer.deployment.waiting.set()
for lbthread in loadBalancerThreads:
	lbthread.join()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
reqHandlerThread.join()

class TestRequests(unittest.TestCase):
	def test_requests(self):
		pod = apiServer.etcd.runningPodList[0]
		self.assertEqual(len(pod.requests), 1)
		pod = apiServer.etcd.runningPodList[1]
		self.assertEqual(len(pod.requests), 3)