#Deployment objects set the configuration and expected number of Pod objects
#label is the label associated with the deployment.
#current_replicas is the number of pods currently running that are associated with 
#the Deployment.
#expected_replicas is the setpoint for the number of pods.
#cpu_cost is the amount of cpu that a pod must be assigned.
#memCost is the amount of memory that a pod must be assigned .

class Deployment:
	def __init__(self, INFOLIST):
		self.deployment_label = INFOLIST[0]
		self.current_replicas = 0
		self.expected_replicas = int(INFOLIST[1])
		self.cpu_cost = int(INFOLIST[2])

	def AddReplicas(self, replicas):
		self.current_replicas += replicas
		print(f"\n\n***Replicas added to {self.deployment_label} Current replicas - {self.current_replicas} Expected replicas - {self.expected_replicas}***")

	def RemoveReplicas(self, replicas):
		self.current_replicas -= replicas
		if self.current_replicas < 0:
			self.current_replicas = 0
		print(f"\n\n!!!Replicas removed from {self.deployment_label} Current replicas - {self.current_replicas} Expected replicas - {self.expected_replicas}")
