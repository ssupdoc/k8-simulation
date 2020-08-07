"""
This tracefile generator is to be used in conjunction with Assignment 1 of CompX529.
It takes a student ID value and an integer seed, from which it generates a tracefile for use
with a simulated Kubernetes cluster
"""

import random

try:
	id = int(input("Enter your student ID: "))
	seed = int(input("Enter seed: "))
except:
	print("Please enter as integer")
	quit()
newSeed = (id*seed)
nodes = []
deployments = []
nodeMax = 3
depMax =  6
depA = 65
depB = 65
commandCount = 20*seed**2
separator = " "

f = open("instructions.txt", "w")
for x in range (1, commandCount+1): #Generates a set number of commands
	commands = ["Sleep"] #Establishes the list of possible commands for this step
	random.seed(newSeed+x)
	if len(nodes) == 0:
		cpus = random.randint(3,5)
		node = "".join(["Node_",str(len(nodes)+1)])
		command = separator.join(["AddNode", node, str(cpus)])
		nodes.append(node)
		f.write(command+"\n") #Node creation will always be the first command
		continue
	elif len(nodes) < nodeMax:#If we have at least one node but can still have more
		commands.append("AddNode")
	if len(deployments) < depMax: #If we can deploy to the cluster
		if depA < 90:
			commands.append("Deploy")
	if len(deployments) > 0:#If we have deployments
		tmpList = commands + ["ReqIn", "ReqIn","ReqIn","ReqIn", "DeleteDeployment", "CrashPod"]
		commands = tmpList
	choice = random.choice(commands) #Select a command from the pool of available options
	if choice == "AddNode":
		cpus = random.randint(3,5)
		node = "".join(["Node_",str(len(nodes)+1)])
		command = separator.join([choice, node, str(cpus)])
		nodes.append(node)
	if choice == "Deploy":
		cpus = random.randint(1,3)
		depLabel = "".join(map(chr,[depA, depB]))
		if depB < 90:
			depB +=1
		else:
			depA +=1
		deployment = "".join(["Deployment_",depLabel])
		command = separator.join([choice, deployment, str(cpus), "1"])
		deployments.append(deployment)	
	if choice == "ReqIn":
		deployment = random.choice(deployments)
		reqTime = random.randint(1,10)
		command = separator.join([choice, str(x), deployment, str(reqTime)])
	if choice == "DeleteDeployment":
		deployment = random.choice(deployments)
		deployments.remove(deployment)
		command = separator.join([choice, deployment])
	if choice == "CrashPod":
		deployment = random.choice(deployments)
		command = separator.join([choice, deployment])
	if choice == "Sleep":
		sleepTime = random.randint(1,5)
		command = separator.join([choice, str(sleepTime)])
	f.write(command+"\n")
	
for deployment in deployments:
	f.write ("DeleteDeployment "+deployment+"\n")
