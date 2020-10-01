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
#Graphing information
depPods1 = []
depPods2 = []
depPods3 = []
depPendPods1 = []
depPendPods2 = []
depPendPods3 = []
dep1PendReqs = []
dep2PendReqs = []
dep3PendReqs = []
stepList = []
#Simulation information
loadBalancers = []
hpas = []
supervisors = []
hpaThreads = []
loadBalancerThreads = []
supervisorThreads = []
count = 0
SEED = "ml_3"
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
		elif cmdAttributes[0] == 'CreateHPA':
			hpa = HPA(apiServer, _hpaCtlLoop, cmdAttributes[1:])
			hpaThread = threading.Thread(target=hpa)
			hpaThread.start()
			hpas.append(hpa)
			hpaThreads.append(hpaThread)
			supervisor = Supervisor(apiServer, hpa)
			supervisorThread = threading.Thread(target=supervisor)
			supervisorThread.start()
			supervisors.append(supervisor)
			supervisorThreads.append(supervisorThread)
		elif cmdAttributes[0] == 'CrashPod':
			apiServer.CrashPod(cmdAttributes[1:])
	#The instructions will sleep after each round of requests. The following code stores values for graphing
	if cmdAttributes[0] == 'Sleep':
		count+=1
		time.sleep(int(cmdAttributes[1]))
		if len(apiServer.etcd.deploymentList) == 1:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(0)
			depPods3.append(0)
			count1 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
			depPendPods1.append(count1)
			depPendPods2.append(0)
			depPendPods3.append(0)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(0)
			dep3PendReqs.append(0)
		elif len(apiServer.etcd.deploymentList) == 2:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(apiServer.etcd.deploymentList[1].expectedReplicas)
			depPods3.append(0)
			count1 = 0
			count2 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count2+=1
			depPendPods1.append(count1)
			depPendPods2.append(count2)
			depPendPods3.append(0)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(len(apiServer.etcd.deploymentList[1].pendingReqs))
			dep3PendReqs.append(0)
		elif len(apiServer.etcd.deploymentList) == 3:
			depPods1.append(apiServer.etcd.deploymentList[0].expectedReplicas)
			depPods2.append(apiServer.etcd.deploymentList[1].expectedReplicas)
			depPods3.append(apiServer.etcd.deploymentList[2].expectedReplicas)
			count1 = 0
			count2 = 0
			count3 = 0
			for pod in apiServer.etcd.pendingPodList:
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[0].deploymentLabel:
					count1+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count2+=1
				if pod.deploymentLabel ==apiServer.etcd.deploymentList[1].deploymentLabel:
					count3+=1
			depPendPods1.append(count1)
			depPendPods2.append(count2)
			depPendPods3.append(count3)
			dep1PendReqs.append(len(apiServer.etcd.deploymentList[0].pendingReqs))
			dep2PendReqs.append(len(apiServer.etcd.deploymentList[1].pendingReqs))
			dep3PendReqs.append(len(apiServer.etcd.deploymentList[2].pendingReqs))
		else:
			depPods1.append(0)
			depPods2.append(0)
			depPods3.append(0)
			depPendPods1.append(0)
			depPendPods2.append(0)
			depPendPods3.append(0)
			dep1PendReqs.append(0)
			dep2PendReqs.append(0)
			dep3PendReqs.append(0)
		#pendReqsList.append(len(apiServer.etcd.pendingReqs))
		stepList.append(count)
time.sleep(5)
print("Shutting down threads")
for hpa in hpas:
	hpa.running = False
	hpa.calibrate.set()
reqHandler.running = False
depController.running = False
scheduler.running = False
nodeController.running = False
apiServer.requestWaiting.set()
for lbthread in loadBalancerThreads:
	lbthread.join()
for hpathread in hpaThreads:
	hpathread	.join()
for supervisorThread in supervisorThreads:
	supervisorThread.join()
depControllerThread.join()
schedulerThread.join()
nodeControllerThread.join()
reqHandlerThread.join()
fig, ((hpa1, hpa2, hpa3), (pp, ap, pr)) = plt.subplots(2,3)
hpa1.plot(hpas[0].xValues, hpas[0].setPoints, color='black', label = 'Setpoint Dep1')
hpa1.plot(hpas[0].xValues, hpas[0].utilValues, color='blue', label = 'CPU util Dep1')
hpa1.set_title('HPA for Deployment 1')
hpa2.plot(hpas[1].xValues, hpas[1].setPoints, color='black', label = 'Setpoint Dep2')
hpa2.plot(hpas[1].xValues, hpas[1].utilValues, color='green', label = 'CPU util Dep2')
hpa2.set_title('HPA for Deployment 2')
hpa3.plot(hpas[2].xValues, hpas[2].setPoints, color='black', label = 'Setpoint Dep3')
hpa3.plot(hpas[2].xValues, hpas[2].utilValues, color='red', label = 'CPU util Dep3')
hpa3.set_title('HPA for Deployment 3')
pp.plot(stepList, depPendPods1, color = 'blue', label = 'Pending Pods Dep1')
pp.plot(stepList, depPendPods2, color = 'green', label = 'Pending Pod Dep2')
pp.plot(stepList, depPendPods3, color = 'red', label = 'Pending Pod Dep3')
ap.plot(stepList, depPods1, color = 'blue', label = 'Active Pods Dep1')
ap.plot(stepList, depPods2, color = 'green', label = 'Active Pods Dep2')
ap.plot(stepList, depPods3, color = 'red', label = 'Active Pods Dep3')
pr.plot(stepList, dep1PendReqs, color='blue', label = 'Pending Requests Dep1')
pr.plot(stepList, dep1PendReqs, color='green', label = 'Pending Requests Dep2')
pr.plot(stepList, dep1PendReqs, color='red', label = 'Pending Requests Dep3')
for ax in fig.get_axes():
	ax.legend()
plt.savefig(f'graph/{SEED}_main.png')

H1_Data = {
	'time': supervisors[0].timestampAudit,
	'Kp': supervisors[0].pValues,
	'Ki': supervisors[0].iValues,
	'avg_error': supervisors[0].avgErrors,
}
h1_df = pd.DataFrame(H1_Data,columns=['time', 'Kp', 'Ki', 'avg_error'])

print(f"List of samples for {supervisors[0].hpa.deploymentLabel}")
print(h1_df)

H2_Data = {
	'time': supervisors[1].timestampAudit,
	'Kp': supervisors[1].pValues,
	'Ki': supervisors[1].iValues,
	'avg_error': supervisors[1].avgErrors
}
h2_df = pd.DataFrame(H2_Data,columns=['time', 'Kp', 'Ki', 'avg_error'])

print(f"List of samples for {supervisors[1].hpa.deploymentLabel}")
print(h2_df)

H3_Data = {
	'time': supervisors[2].timestampAudit,
	'Kp': supervisors[2].pValues,
	'Ki': supervisors[2].iValues,
	'avg_error': supervisors[2].avgErrors
}
h3_df = pd.DataFrame(H3_Data,columns=['time', 'Kp', 'Ki', 'avg_error'])

print(f"List of samples for {supervisors[2].hpa.deploymentLabel}")
print(h3_df)

fig, ((h1, h2, h3)) = plt.subplots(1,3, subplot_kw={"projection": "3d"}, figsize=(16, 8))
h1.scatter(h1_df['Kp'], h1_df['Ki'], h1_df['avg_error'], color='blue')
h1.set_xlabel('Kp')
h1.set_ylabel('Ki')
h1.set_zlabel('avg_error')
h2.scatter(h2_df['Kp'], h2_df['Ki'], h2_df['avg_error'], color='blue')
h2.set_xlabel('Kp')
h2.set_ylabel('Ki')
h2.set_zlabel('avg_error')
h3.scatter(h3_df['Kp'], h3_df['Ki'], h3_df['avg_error'], color='blue')
h3.set_xlabel('Kp')
h3.set_ylabel('Ki')
h3.set_zlabel('avg_error')

plt.savefig(f'graph/{SEED}_errors.png')
