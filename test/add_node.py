from src.api_server import APIServer
import unittest
import time

apiServer = APIServer()

instructions = open("tracefiles/add_node.txt", "r")
commands = instructions.readlines()
for command in commands:
	cmdAttributes = command.split()
	print(str(cmdAttributes))
	with apiServer.etcdLock:
		if cmdAttributes[0] == 'AddNode':
			apiServer.CreateWorker(cmdAttributes[1:])
	time.sleep(3)
time.sleep(5)


class TestAddWorker(unittest.TestCase):
	def test_workers_length(self):
		self.assertEqual(len(apiServer.GetWorkers()), 1)

	def test_worker_data(self):
		worker = apiServer.etcd.nodeList[0]
		self.assertEqual(worker.assigned_cpu, 4)
		self.assertEqual(worker.available_cpu, 4)
		