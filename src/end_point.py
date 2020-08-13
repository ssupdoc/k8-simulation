#EndPoint objects associate a Pod with a Deployment and a Node.
#pod is the Pod.
#deployment_label is the label of the Deployment.
#node is the Node.

class EndPoint:

	def __init__(self, pod, node):
		self.pod = pod
		self.deployment_label = self.pod.deployment_label
		self.node = node
