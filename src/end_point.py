#EndPoint objects associate a Pod with a Deployment and a Node.
#pod is the Pod.
#deploymentLabel is the label of the Deployment.
#node is the Node.

class EndPoint:

	def __init__(self, pod, node):
		self.pod = pod
		self.deploymentLabel = self.pod.deploymentLabel
		self.node = node
