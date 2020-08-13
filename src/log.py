from time import time
import logging
import os

REQUEST_SUCCESS = "PROCESSED"
REQUEST_FAILURE = "FAILED"

class Log:
	def __init__(self, TRACEFILE):
		self.requests = []
		self.deployments = []
		self.pod_list = []
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
		logging.info("------------------------------")
		for req in self.requests:
			logging.info(f"Req {req.label} - Execution time {req.exec_time}s took {round(req.throughput, 4)}s STATUS: {req.status}")
		logging.info("------------------------------")

	def LogRequestSuccessFailure(self):
		self.LogReqSuccess()
		self.LogRequestFailure()

	def LogRequestFailure(self):
		logging.info("----- Request Failure -----")
		logging.info("------------------------------")
		failed_requests = self.GetFailureRequests(self.requests)
		logging.info(f"Failed requests: {len(failed_requests)}/{len(self.requests)}")
		logging.info(f"Average wait time of failed requests: {round(self.CalculateAverageWaitTime(failed_requests), 4)}s")
		logging.info("------------------------------")

	def LogReqSuccess(self):
		logging.info("----- Request Success -----")
		logging.info("------------------------------")
		successful_requests = self.GetSuccessfulRequests(self.requests)
		logging.info(f"Successful requests: {len(successful_requests)}/{len(self.requests)}")
		logging.info(f"Average wait time of successful requests: {round(self.CalculateAverageWaitTime(successful_requests), 4)}s")
		logging.info("------------------------------")

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
		logging.info("------------------------------")
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
		logging.info("------------------------------")


	def GetRequestsByDeployment(self, label):
		return list(filter(lambda req: req.deployment_label == label, self.requests))

	def AddPod(self, pod):
		pod.req_count = 0
		self.pod_list.append(pod)

	def AddRequestHandlingPod(self, pod):
		matching_pod = next(filter(lambda existing_pod: existing_pod.pod_name == pod.pod_name, self.pod_list), None)
		if hasattr(matching_pod, 'req_count'):
			matching_pod.req_count += 1
		else:
			matching_pod.req_count = 1

	def LogPodRequestHandlingMetrics(self):
		logging.info("----- Pod list by max requests handled -----")
		logging.info("--------------------------------------------")
		sorted_pod_list = sorted(self.pod_list, key=lambda pod: pod.req_count, reverse=True)
		for pod in sorted_pod_list:
			logging.info(f"Pod {pod.pod_name} Requests handled: {pod.req_count}")
		logging.info("---------------------------------------------")

	def LogMetrics(self):
		self.LogRequestThroughput()
		self.LogRequestSuccessFailure()
		self.LogDeploymentWiseMetrics()
		self.LogPodRequestHandlingMetrics()