from src.api_server import APIServer
from src.hpa import HPA
'''
Your supervisory controller will analyse the trend of the error produced by your HPA controller
Your calibration of Kp and Ki should be based on linear regression following e = a.Kp+b.Ki+c
Based on your regression findings, you should adjust the Kp and Ki values of the HPA controller to minimise the error produced.
The role of your supervisor is to optimise the performance of your HPA controller.
'''
class Supervisor:
	def __init__(self, APIServer, HPA):
		self.hpa = HPA
		self.apiServer = APIServer
		self.pValues = []
		self.iValues = []
		self.avgErrors = []
		self.indexes = []
		self.running = True
		self.index =0
	def __call__(self):
		while self.running:
			self.index+=1
			self.hpa.calibrate.wait()
			with self.apiServer.etcdLock:
				if self.hpa.running==False:
					self.running = False
					break
				self.hpa.calibrate.clear()
				self.pValues.append(self.hpa.pValue)
				self.iValues.append(self.hpa.iValue)
				self.avgErrors.append(sum(self.hpa.errors)/len(self.hpa.errors))
				self.hpa.errors.clear()
		print('Supervisor Shutdown')
				#PERFORM YOUR REGRESSION HERE
				
