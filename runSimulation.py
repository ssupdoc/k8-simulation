import threading
from src.request import Request
from src.dep_controller import DepController
from src.api_server import APIServer
from src.req_handler import ReqHandler
from src.node_controller import NodeController
from src.scheduler import Scheduler
from src.hpa import HPA
from src.load_balancer import LoadBalancer
import time
import matplotlib.pyplot as plt
import sys

TRACEFILE_NAME = "seed3_instructions"

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

class LoadBalancerAudit:
	def __init__(self, loadBalancer, lbThread):
		self.loadBalancer = loadBalancer
		self.lbThread = lbThread

class HPAAudit:
	def __init__(self, hpa, hpaThread):
			self.hpa = hpa
			self.hpaThread = hpaThread

def CleanupDeployments():
	for deployment in apiServer.etcd.deploymentList:
		TerminateLoadBalancer(deployment)
		TerminateHPA(deployment)

def TerminateLoadBalancer(deployment):
	lb = next(filter(lambda lb: lb.loadBalancer.deployment.deploymentLabel == deployment.deploymentLabel, loadBalancers), None)
	if lb is not None:
		lb.loadBalancer.running = False
		lb.loadBalancer.deployment.waiting.set()
		lb.lbThread.join()

def PlotGraph():
	plotNum = 221
	plt.figure(1, figsize=(14,10))
	for hpaAudit in hpaList:
		plt.subplot(plotNum)
		plt.title(hpaAudit.hpa.deploymentLabel)
		plt.xlabel('Time')
		plt.ylabel('Average load (%)')
		plt.plot(hpaAudit.hpa.graph.time, hpaAudit.hpa.graph.setPoint, label="Set Point (y)")
		plt.plot(hpaAudit.hpa.graph.time, hpaAudit.hpa.graph.output, label="Output (y)")
		plt.legend(loc="upper left")
		plotNum += 1
	ctrlTitle = "-".join(map(str, ctrlValues))
	plt.savefig(f'graph/output_{TRACEFILE_NAME}_{ctrlTitle}_{LOADBALANCERTYPE}_{CONTROLLERTYPE}.png')

def TerminateHPA(deployment):
	hpaAudit = next(filter(lambda hpaAudit: hpaAudit.hpa.deploymentLabel == deployment.deploymentLabel, hpaList), None)
	if hpaAudit is not None:
		hpaAudit.hpa.running = False
		hpaAudit.hpaThread.join()

#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 2
_depCtlLoop = 2
_scheduleCtlLoop =2
_hpaCtlLoop =2

hpaList = []

loadBalancers = []
# Load balancer type ['round_robin', 'utilisation_aware']
LOADBALANCERTYPE = 'round_robin'

# Controller type ['pid', 'pi']
CONTROLLERTYPE = 'pid'

ctrlValues = [0, 0, 0]

if(len(sys.argv) > 1):
	ctrlValues = sys.argv[1:]
	if CONTROLLERTYPE == 'pi' and len(ctrlValues) == 3:
		ctrlValues[2] = 0

apiServer = APIServer(ctrlValues=ctrlValues)
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
instructions = open(f"tracefiles/{TRACEFILE_NAME}.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	# print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'Deploy':
			apiServer.CreateDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			loadBalancer = LoadBalancer(apiServer, deployment, LOADBALANCERTYPE)
			lbThread = threading.Thread(target=loadBalancer)
			lbThread.start()
			loadBalancers.append(LoadBalancerAudit(loadBalancer, lbThread))
		elif cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'DeleteDeployment':
			apiServer.RemoveDeployment(cmdAttributes[1:])
			deployment = apiServer.GetDepByLabel(cmdAttributes[1])
			TerminateLoadBalancer(deployment)
			TerminateHPA(deployment)
		elif cmdAttributes[0] == 'ReqIn':
			apiServer.PushReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CreateHPA':
			hpa = HPA(apiServer, _hpaCtlLoop, cmdAttributes[1:])
			hpaThread = threading.Thread(target=hpa)
			hpaThread.start()
			hpaList.append(HPAAudit(hpa, hpaThread))
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	if cmdAttributes[0] == 'Sleep':
			time.sleep(int(cmdAttributes[1]))
	#printStates(output, apiServer)
	time.sleep(0)
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
PlotGraph()
CleanupDeployments()