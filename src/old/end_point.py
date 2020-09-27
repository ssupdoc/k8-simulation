#EndPoint objects associate a Pod with a Deployment and a Node.
#pod is the associated Pod.
#deploymentLabel is the label of the Deployment.
#node is the associated Node
#flag is the priority of the endpoint for request routing [0,1].

class EndPoint:

	def __init__(self, POD, DEPLABEL, NODE):
		self.pod = POD
		self.deploymentLabel = DEPLABEL
		self.node = NODE
		flag = 0
