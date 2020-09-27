import threading
import time
from src.measurement_graph import MeasurementGraph

#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
		self.deploymentLabel = INFOLIST[0]
		self.setPoint = int(INFOLIST[1])
		self.syncPeriod = int(INFOLIST[2])
		self.lastSync = time.time()
		self.averageLoad = 0
		self.loadMetrics = []
		self.graph = MeasurementGraph()
		self.prevState = {'t': 0, 'p': 0}
	
	def __call__(self):
		print("HPA start for deployment " + self.deploymentLabel)
		while self.running:
			deployment = self.apiServer.GetDepByLabel(self.deploymentLabel)
			if deployment is not None:
				ctrl = self.apiServer.controller
				endPoints = self.apiServer.GetEndPointsByLabel(self.deploymentLabel)
				if len(endPoints):
					_deploymentLoad = 0
					for endPoint in endPoints:
						_deploymentLoad += self.getLoadForPod(endPoint.pod)
					depAvgLoad = _deploymentLoad / len(endPoints)
					self.loadMetrics.append(depAvgLoad)

				self.averageLoad = self.getAverageLoad(self.loadMetrics.copy())
				self.graph.record(self.setPoint, self.averageLoad, deployment)

				curTime = time.time()
				if int(curTime - self.lastSync) >= self.syncPeriod: # Check if the sliding window has expired
					self.lastSync = time.time()
					self.loadMetrics = []

					# If load fails to be within +-10% of setpoint
					if self.calcAbsErrorPerc(self.setPoint, self.averageLoad) > 10:
						ctrl.SetState(self.prevState['t'], self.prevState['p']) # Previous state update in HPA
						ctrlOutput = ctrl.work(self.averageLoad - self.setPoint)
						ctrlDirection = ctrlOutput['y']
						self.prevState['t'] = ctrlOutput['t']
						self.prevState['p'] = ctrlOutput['p']
						# Pod increment/decrement based on ctrl direction
						if ctrlDirection <= 0:
							deployment.expectedReplicas -= 1
						else:
							deployment.expectedReplicas += 1
						if deployment.expectedReplicas <= 0: # expected replicas can never be less than 1
								deployment.expectedReplicas = 1
			time.sleep(self.time)
		print("HPA shutdown deployment " + self.deploymentLabel)

	# Returns the load calculated for pod utilisation in percentage
	def getLoadForPod(self, pod):
		load = 0
		if pod:
			# requests length is the same as the difference between assigned and available CPU
			load = len(pod.requests)/pod.assigned_cpu
		return (load * 100) #return load in percentage

	# Returns the average load for a given load metric rounded to the nearest whole number
	def getAverageLoad(self, loadMetrics):
		if len(loadMetrics):
			sum = 0
			for metric in loadMetrics:
				sum += metric
			averageLoad = sum / len(loadMetrics)
			return round(averageLoad)
		return 0

	def calcAbsErrorPerc(self, setPoint, actualVal):
		return abs((setPoint - actualVal)/setPoint * 100)
