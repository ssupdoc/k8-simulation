from time import time
import logging
import os

class Log:
	def __init__(self, TRACEFILE):
		self.requests = []
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

	def LogMetrics(self):
		self.LogRequestThroughput()