from api_server import APIServer
import time

#reqHandler is a thread that continuously checks the pendingRequest queue and calls an associated pod to handle the incoming request.

class ReqHandler:
	def __init__(self, api_server):
		self.api_server = api_server
		self.running = True
	
	def __call__(self):
		print("reqHandler start")
		while self.running:
			self.api_server.request_waiting.wait()
			with self.api_server.etcd_lock:
				pending_req_list = []
				pending_req_list[:] = self.api_server.GetPendingRequests()
				for req in pending_req_list:
					matching_end_point_list = self.api_server.GetEndPointsByLabel(req.deployment_label)
					pods_active = any(not end_point.pod.IsTerminating() for end_point in matching_end_point_list)
					if pods_active: # Check whether atleast one pod is non-terminating, else discard request
						suitable_pod = self.GetPodForRequest(req, matching_end_point_list)
						if suitable_pod:
							self.api_server.EngagePod(suitable_pod, req)
							self.api_server.DiscardRequest(req, "PROCESSED")
					else:
						self.api_server.DiscardRequest(req, "FAILED")
			self.api_server.request_waiting.clear()
		print("ReqHandlerShutdown")

	def GetPodForRequest(self, req, end_point_list):
		suitable_pod = None
		for end_point in end_point_list:
			if self.api_server.CheckEndPoint(end_point):
				pod = self.api_server.GetPod(end_point)
				if pod.HasAvailableCPU():
					suitable_pod = pod
					break
		return suitable_pod
