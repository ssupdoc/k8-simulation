from time import time
import logging
import os

REQUEST_SUCCESS = "PROCESSED"
REQUEST_FAILURE = "FAILED"

class Log:
	def __init__(self, TRACEFILE):
		self.requests = []
		self.deployments = []
		self.log_file = self.GetLogFilePath(TRACEFILE)
		logging.basicConfig(filename=self.log_file, level=logging.INFO)

	def GetLogFilePath(self, TRACEFILE):
		file_name = TRACEFILE.split('.')
		path =  os.getcwd() + f"/logs/{file_name[0]}.log"
		return path

	def AddRequest(self, req):
		req.start_time = time()
		self.requests.append(req)

	def UpdateRequest(self, req_label, status):
		req = next(filter(lambda req: req.label == req_label, self.requests), None)
		if req is not None:
			req.end_time = time()
			req.throughput = req.end_time - req.start_time
			req.status = status

	def LogRequestThroughput(self):
		logging.info("----- Request throughput -----")
		for req in self.requests:
			logging.info(f"Req {req.label} - Execution time {req.exec_time}s took {round(req.throughput, 4)}s STATUS: {req.status}")

	def LogRequestSuccessFailure(self):
		self.LogReqSuccess()
		self.LogRequestFailure()

	def LogRequestFailure(self):
		logging.info("----- Request Failure -----")
		failed_requests = self.GetFailureRequests(self.requests)
		logging.info(f"Failed requests: {len(failed_requests)}/{len(self.requests)}")
		logging.info(f"Average wait time of failed requests: {round(self.CalculateAverageWaitTime(failed_requests), 4)}s")

	def LogReqSuccess(self):
		logging.info("----- Request Success -----")
		successful_requests = self.GetSuccessfulRequests(self.requests)
		logging.info(f"Successful requests: {len(successful_requests)}/{len(self.requests)}")
		logging.info(f"Average wait time of successful requests: {round(self.CalculateAverageWaitTime(successful_requests), 4)}s")

	def CalculateAverageWaitTime(self, requests):
		total_wait_time = 0
		for req in requests:
			if req.status is REQUEST_SUCCESS:
				total_wait_time += (req.throughput - req.exec_time)
			elif req.status is REQUEST_FAILURE:
				total_wait_time += req.throughput
		average_wait_time = 0
		if requests:
			average_wait_time = total_wait_time / len(requests)
		return average_wait_time
	
	def GetSuccessfulRequests(self, requests):
		return list(filter(lambda req: req.status == REQUEST_SUCCESS, requests))

	def GetFailureRequests(self, requests):
		return list(filter(lambda req: req.status == REQUEST_FAILURE, requests))

	def AddDeployment(self, deployment):
		self.deployments.append(deployment)

	def LogDeploymentWiseMetrics(self):
		logging.info("----- Deployment wise metrics -----")
		for deployment in self.deployments:
			requests_in_deployment = self.GetRequestsByDeployment(deployment.deployment_label)
			logging.info(f"Deployment label: {deployment.deployment_label} with {len(requests_in_deployment)} requests")
			total_average_wait_time = self.CalculateAverageWaitTime(requests_in_deployment)
			logging.info(f"Average wait time of requests: {round(total_average_wait_time, 3)}s")
			successful_req = self.GetSuccessfulRequests(requests_in_deployment)
			success_perc = 0
			if successful_req:
				success_perc = len(successful_req)/len(requests_in_deployment) * 100
			logging.info(f"Successful requests: {success_perc}%")


	def GetRequestsByDeployment(self, label):
		return list(filter(lambda req: req.deployment_label == label, self.requests))


	def LogMetrics(self):
		self.LogRequestThroughput()
		self.LogRequestSuccessFailure()
		self.LogDeploymentWiseMetrics()