#EndPoint objects associate a Pod with a Deployment and a Node.
#podName is the name of the Pod.
#deploymentLabel is the label of the Deployment.
#nodeLabel is the label of the Node.
#flag is the priority of the endpoint for request routing [0,1].

class EndPoint:

	def __init__(self, POD, DEPLABEL, NODE):
		self.pod = POD
		self.deploymentLabel = DEPLABEL
		self.node = NODE
		flag = 0
