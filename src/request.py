#Requests stress Pod resources for a given period of time to simulate load
#label is the request label
#deployment_label is the Deployment that the request is beings sent to
#exec_time is how long the request will use those resource for before completing
#status the status of the request ['PENDING', 'PROCESSING', 'FAILED']
class Request:
	def __init__(self, INFOLIST):
		self.label = INFOLIST[0]
		self.deployment_label = INFOLIST[1]
		self.exec_time = int(INFOLIST[2])

