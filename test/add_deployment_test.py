from src.api_server import APIServer
import unittest
import time

apiServer = APIServer()

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


class TestAddDeployment(unittest.TestCase):
	def test_deployment_length(self):
		self.assertEqual(len(apiServer.GetDeployments()), 1)

	def test_deployment_data(self):
		deployment = apiServer.etcd.deploymentList[0]
		self.assertEqual(deployment.expectedReplicas, 2)
		self.assertEqual(deployment.cpuCost, 2)
		