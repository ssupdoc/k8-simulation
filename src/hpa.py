import threading
import time

#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
		self.deploymentLabel = INFOLIST[0]
		self.setPoint = INFOLIST[1]
		self.syncPeriod = int(INFOLIST[2])
		self.lastSync = time.time()
		self.averageLoad = 0
		self.loadMetrics = []
	
	def __call__(self):
		while self.running:
			ctrl = self.apiServer.controller
			endPoints = self.apiServer.GetEndPointsByLabel(self.deploymentLabel)
			if len(endPoints):
				_deploymentLoad = 0
				for endPoint in endPoints:
					_deploymentLoad += self.getLoadForPod(endPoint.pod)
				depAvgLoad = _deploymentLoad / len(endPoints)
				self.loadMetrics.append(depAvgLoad)

			curTime = time.time()
			if int(curTime - self.lastSync) >= self.syncPeriod:
				self.averageLoad = self.getAverageLoad(self.loadMetrics)
				print(f'Average load of {self.deploymentLabel}:  {self.averageLoad}')
				self.lastSync = time.time()
				self.loadMetrics = []

			time.sleep(self.time)

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
