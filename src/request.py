from api_server import APIServer

#Requests stress Pod resources for a given period of time to simulate load
#deploymentLabel is the Deployment that the request is beings sent to
#cpuCost is the number of threads that the request will use on a pod
#duration is how long the request will use those resource for before completing
class Request:
	def __init__(self, APISERVER, INFOLIST):
		self.deploymentLabel = INFOLIST[0]
		self.cpuCost = INFOLIST[1]
		self.execTime = INFOLIST[3]
