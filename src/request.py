#Requests stress Pod resources for a given period of time to simulate load
#label is the request label
#deploymentLabel is the Deployment that the request is beings sent to
#execTime is how long the request will use those resource for before completing
#status the status of the request ['PENDING', 'PROCESSED', 'FAILED']
class Request:
	def __init__(self, INFOLIST):
		print('\n\n\n***Req In desc starts****')
		for info in INFOLIST:
			print(info)
		print('***Req In desc ends***\n\n\n')
		self.label = INFOLIST[0]
		self.deploymentLabel = INFOLIST[1]
		self.execTime = int(INFOLIST[2])
		self.status = 'PENDING'
	
	def SetStatus(self, status):
		self.status = status
