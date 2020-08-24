import threading
from request import Request
from dep_controller import DepController
from api_server import APIServer
from req_handler import ReqHandler
from node_controller import NodeController
from scheduler import Scheduler
#from hpa import HPA
#from load_balancer import LoadBalancer
import time


def printStates(f, apiServer):
	with apiServer.etcdLock:
		Pending = apiServer.GetPending()
		Nodes = apiServer.GetWorkers()
		EndPoints = apiServer.GetEndPoints()
		Deployments = apiServer.GetDeployments()
		f.write("\n---NODES---\n")
		for node in Nodes:
			f.write(str(node.label)+" AVAILABLE CPU: "+str(node.available_cpu)+" ASSIGNED CPU: "+str(node.assigned_cpu)+"\n")
		f.write("\n---DEPLOYMENTS---\n")
		for dep in Deployments:
			f.write(str(dep.deploymentLabel)+" COST: "+str(dep.cpuCost)+" EXPECTED REPLICAS: "+str(dep.expectedReplicas)+" CURRENT: "+str(dep.currentReplicas)+"\n")
		f.write("\n---ENDPOINTS---\n")
		for ep in EndPoints:
			f.write(str(ep.deploymentLabel)+" NODE: "+str(ep.node.label)+" POD: "+str(ep.pod.podName)+"\n")
		f.write("\n---PENDING PODS---\n")
		for pod in Pending:
			f.write(str(pod.podName)+"\n")
		f.write("\n")

#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

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

#output = open("output.txt", "w")
instructions = open("instructions.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabelcmdAttributes[1]
			#loadbalancer = LoadBalancer(apiServer, deployment)
			#lbThread = threading.Thread(target=loadbalancer)
			#lbThread.start()
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			apiServer.RemoveDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		#elif cmdAttributes[0] == 'CreateHPA':
			#hpa = HPA(apiServer, _hpaCtlLoop, cmdAttributes[1:])
			#hpaThread = threading.Thread(target=hpa)
			#hpaThread.start()
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	if cmdAttributes[0] == 'Sleep':
			time.sleep(int(cmdAttributes[1]))
	#printStates(output, apiServer)
	time.sleep(3)
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