#The WorkerNode is the object to which pods can be scheduled
#label is the label of the Node
#assigned_cpu is the amount of cpu assigned to the node
#assigned_mem is the amount of memory assigned to the node
#available_cpu is the amount of assigned_cpu not currently in use
#available_mem is the amount of assigned_mem not currently in use
#status communicates the Node's availability. ['UP', 'CRASHED', 'TERMINATING', 'TERMINATED']
#podList is the internal list of Pod objects that are currently deployed on the Node

class WorkerNode:


	def __init__(self, INFOLIST):
		self.label = INFOLIST[0]
		self.assigned_cpu = int(INFOLIST[1])
		self.available_cpu = int(self.assigned_cpu)
		self.status = 'UP'

	def AllocateCpu(self, cpuCost):
		if cpuCost <= self.available_cpu:
			self.available_cpu -= cpuCost
		print(f"***Worker node {self.label} allocated: Assigned - {self.assigned_cpu} Available - {self.available_cpu}***")

	def deallocateCpu(self, cpuCost):
		self.available_cpu += cpuCost
		if self.available_cpu > self.assigned_cpu:
			self.available_cpu = self.assigned_cpu
		print(f"***Worker node {self.label} deallocated: Assigned - {self.assigned_cpu} Available - {self.available_cpu}***")
