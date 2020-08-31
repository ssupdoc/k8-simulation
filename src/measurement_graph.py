import time

class MeasurementGraph:
	def __init__(self):
		self.initTime = time.time()
		self.time = []
		self.setPoint = []
		self.output = []
	def record(self, setPoint, output):
		self.time.append(round(time.time() -  self.initTime))
		self.setPoint.append(setPoint)
		self.output.append(output)