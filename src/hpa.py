import threading
import time
from src.MyController import PIDController
#Your Horizontal Pod Autoscaler should monitor the average resource utilization of a deployment across
#the specified time period and execute scaling actions based on this value. The period can be treated as a sliding window.

class HPA:
	def __init__(self, APISERVER, LOOPTIME, INFOLIST):
		self.apiServer = APISERVER
		self.running = True
		self.time = LOOPTIME
		self.deploymentLabel = INFOLIST[0]
		self.setPoint = float(INFOLIST[1])/100
		self.syncPeriod = int(INFOLIST[2])
		self.calibratePeriod = int(INFOLIST[3])
		self.averages = []
		self.errors = []
		self.maxReps = 25
		self.minReps = 1
		self.pValue = 1
		self.iValue = 1
		self.loopCount = 0
		self.periods = 0
		self.controller = PIDController(self.pValue, self.iValue, 0)
		self.calibrate = threading.Event()
		self.xValues = []
		self.setPoints = []
		self.utilValues = []
	def __call__(self):
		print('HPA Start')
		counts = 0
		while self.running:
			with self.apiServer.etcdLock:
				deployment = self.apiServer.GetDepByLabel(self.deploymentLabel)
				if deployment == None:
					self.running = False
					break
				windowLength = int(self.syncPeriod/self.time)
				pods = []
				u = 0
				for pod in self.apiServer.etcd.pendingPodList:
					if pod.deploymentLabel == self.deploymentLabel:
						pods.append(pod)
				for pod in self.apiServer.etcd.runningPodList:
					if pod.deploymentLabel == self.deploymentLabel:
						pods.append(pod)
				if len(self.averages) >= windowLength:
					self.averages.pop(0)
				availableCPUS = 0
				for pod in pods:
					availableCPUS+=pod.available_cpu
				if len(pods) == 0:
					print('NO PODS')
					averageUtil = 0
				else:
					averageUtil = (deployment.cpuCost*len(pods)-availableCPUS)/(deployment.cpuCost*len(pods))
				self.averages.append(averageUtil)
				periodAvg = sum(self.averages)/len(self.averages)
				error = periodAvg-self.setPoint
				#print('\n')
				#print(self.deploymentLabel+" AVG: "+str(averageUtil))
				#print(self.deploymentLabel+" PERIOD AVG: "+str(periodAvg))
				#print(self.deploymentLabel+" Error: "+str(error))
				self.errors.append(error)
				if abs(error)>0.1:
					u = int(self.controller.work(error))
					#print(self.deploymentLabel+ " U: "+str(u))
					#print(self.deploymentLabel+" "+str(deployment.currentReplicas)+"/"+str(deployment.expectedReplicas))
				if u > 0:
					if deployment.expectedReplicas + u > self.maxReps:
						deployment.expectedReplicas = self.maxReps
					else:
						deployment.expectedReplicas += u
				if u < 0:
					if deployment.expectedReplicas + u < self.minReps:
						deployment.expectedReplicas = self.minReps
					else:
						deployment.expectedReplicas += u
				counts+=1
				#Save information for graphing
				self.xValues.append(counts)
				self.setPoints.append(self.setPoint)
				self.utilValues.append(periodAvg)
			self.loopCount+=1
			if self.loopCount == windowLength:
				self.loopCount = 0
				self.periods+=1
			#Call our supervisor if we require calibration
			if self.periods == self.calibratePeriod:
				self.calibrate.set() 
				self.periods = 0
			time.sleep(self.time)
		print("HPA Shutdown")
