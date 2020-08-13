import threading
from request import Request
from dep_controller import DepController
from api_server import APIServer
from req_handler import ReqHandler
from node_controller import NodeController
from scheduler import Scheduler
import time

#This is the simulation frontend that will interact with your APIServer to change cluster configurations and handle requests
#All building files are guidelines, and you are welcome to change them as much as desired so long as the required functionality is still implemented.

_nodeCtlLoop = 5
_depCtlLoop = 5
_scheduleCtlLoop =5

api_server = APIServer()
dep_controller = DepController(api_server, _depCtlLoop)
node_controller = NodeController(api_server, _nodeCtlLoop)
req_handler = ReqHandler(api_server)
scheduler = Scheduler(api_server, _scheduleCtlLoop)
dep_controller_thread = threading.Thread(target=dep_controller)
node_controller_thread = threading.Thread(target=node_controller)
req_handler_thread = threading.Thread(target=req_handler)
scheduler_thread = threading.Thread(target = scheduler)
print("Threads Starting")
req_handler_thread.start()
node_controller_thread.start()
dep_controller_thread.start()
scheduler_thread.start()
print("ReadingFile")

instructions = open("instructions.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	with api_server.etcd_lock:
		if cmdAttributes[0] == 'Deploy':
			api_server.CreateDeployment(cmdAttributes[1:])
		elif cmdAttributes[0] == 'AddNode':
			api_server.CreateWorker(cmdAttributes[1:])
		elif cmdAttributes[0] == 'CrashPod':
			api_server.CrashPod(cmdAttributes[1])
		elif cmdAttributes[0] == 'DeleteDeployment':
			api_server.RemoveDeployment(cmdAttributes[1])
		elif cmdAttributes[0] == 'ReqIn':
			api_server.AddReq(cmdAttributes[1:])
		elif cmdAttributes[0] == 'Sleep':
			time.sleep(int(cmdAttributes[1]))
	time.sleep(5)
time.sleep(5)
print("Shutting down threads")

req_handler.running = False
dep_controller.running = False
scheduler.running = False
node_controller.running = False
api_server.request_waiting.set()
dep_controller_thread.join()
scheduler_thread.join()
node_controller_thread.join()
req_handler_thread.join()