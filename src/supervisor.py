from src.api_server import APIServer
# from src.hpa import HPA
import pandas as pd
import random
import matplotlib.pyplot as plt
from sklearn import linear_model
import statsmodels.api as sm
from sklearn.model_selection import train_test_split
from sklearn.model_selection import LeaveOneOut
import time
CONSTRAINT = 0.1
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
		self.timestampAudit = []
		self.indexes = []
		self.running = True
		self.index =0
		self.regr = None
		self.initialTimeStamp = time.time()
		self.scoreList = []
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
				self.timestampAudit.append(round(time.time() - self.initialTimeStamp))
				self.hpa.errors.clear()
				if(len(self.pValues) > 10):
					self.performRegression()
				else:
					(self.hpa.pValue, self.hpa.iValue)  = self.assignRandomValues(self.hpa.pValue, self.hpa.iValue)

		print('Supervisor Shutdown')
		
	def performRegression(self):
		HPA_DATA = {
			'Kp': self.pValues,
			'Ki': self.iValues,
			'avg_error': self.avgErrors
		}
		df = pd.DataFrame(HPA_DATA,columns=['Kp', 'Ki', 'avg_error'])
		X = df[['Kp','Ki']]
		Y = df['avg_error']
		
		X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
		self.regr = linear_model.LinearRegression()
		self.regr.fit(X_train, y_train)

		score = self.regr.score(X_test, y_test)
		self.scoreList.append(score)
		print(f"Score for supervisor {self.hpa.deploymentLabel} is {score}")
			

	def assignRandomValues(self, prevP, prevI):
		dp = round(random.uniform(-CONSTRAINT, CONSTRAINT), 2)
		di = self.randomiseSign(CONSTRAINT - abs(dp))
		newP = prevP + dp
		newI = prevI + di
		if self.checkConstraint(prevP,newP, prevI, newI):
			if newP < 0:
				newP = 0
			if newI < 0:
				newI = 0
			if newP == 0 and newI == 0:
				(newP,newI) = self.assignRandomValues(prevP, prevI)
		return (newP, newI)

	def randomiseSign(self, value):
		signConst = 1
		firstDecimal = int(value*10)
		if firstDecimal % 2 == 0:
			firstDecimal = -1
		return value * signConst
	
	def checkConstraint(self, prevP, prevI, newP, newI):
		if ((abs(newP - prevP) + abs(newI - prevI)) > CONSTRAINT):
			return False
		return True
				
