from api_server import APIServer
import time

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler:
	def __init__(self, APISERVER):
		self.apiServer = APISERVER
		self.running = True
	
	def __call__(self):
		print("reqHandler start")
		while self.running:
			self.apiServer.requestWaiting.wait()
			with self.apiServer.etcdLock:
				pending_req_list = []
				pending_req_list[:] = self.apiServer.GetPendingRequests()
				for req in pending_req_list:
					matching_end_point_list = self.apiServer.GetEndPointsByLabel(req.deploymentLabel)
					pods_active = any(not end_point.pod.IsTerminating() for end_point in matching_end_point_list)
					if pods_active: # Check whether atleast one pod is non-terminating, else discard request
						suitable_pod = self.GetPodForRequest(req, matching_end_point_list)
						if suitable_pod:
							suitable_pod.HandleRequest(req)
							req.SetStatus("PROCESSING")
							self.apiServer.DiscardRequest(req)
					else:
						req.SetStatus("FAILED")
						self.apiServer.DiscardRequest(req)
			self.apiServer.requestWaiting.clear()
		print("ReqHandlerShutdown")

	def GetPodForRequest(self, req, end_point_list):
		suitable_pod = None
		for end_point in end_point_list:
			if self.apiServer.CheckEndPoint(end_point):
				pod = self.apiServer.GetPod(end_point)
				if pod.HasAvailableCPU():
					suitable_pod = pod
					break
		return suitable_pod
