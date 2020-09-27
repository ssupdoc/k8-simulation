import time

class MeasurementGraph:
	def __init__(self):
		self.initTime = time.time()
		self.time = []
		self.setPoint = []
		self.output = []
		self.expectedReplicas = []
		self.currentReplicas = []
	def record(self, setPoint, output, deployment):
		self.time.append(round(time.time() -  self.initTime))
		self.setPoint.append(setPoint)
		self.output.append(output)
		self.expectedReplicas.append(deployment.expectedReplicas)
		self.currentReplicas.append(deployment.currentReplicas)