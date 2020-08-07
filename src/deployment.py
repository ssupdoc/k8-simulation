#Deployment objects set the configuration and expected number of Pod objects
#label is the label associated with the deployment.
#currentReplicas is the number of pods currently running that are associated with 
#the Deployment.
#expectedReplicas is the setpoint for the number of pods.
#cpuCost is the amount of cpu that a pod must be assigned.
#memCost is the amount of memory that a pod must be assigned .

class Deployment:
	def __init__(self, INFOLIST):
		self.deploymentLabel = INFOLIST[0]
		self.currentReplicas = 0
		self.expectedReplicas = int(INFOLIST[1])
		self.cpuCost = int(INFOLIST[2])
