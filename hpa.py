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
		self.syncPeriod = INFOLIST[2]
	
	def __call__(self):
		deployment = self.apiServer.GetDepByLabel(self.deploymentLabel)
		ctrl = self.apiServer.controller
		
		time.sleep(self.time)
