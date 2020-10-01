"""
This tracefile generator is to be used in conjunction with Assignment 4 of CompX529.
It takes a student ID value and an integer seed, from which it generates a tracefile for use
with a simulated Kubernetes cluster


EDIT PARAMETERS WITHIN "CreateHPA" INSTRUCTION BLOCK AT BOTTOM OF FILE FOR CALIBRATION BEHAVIOURS.
CHANGE PARAMETERS BELOW TRY BLOCK FOR OTHER BEHAVIOURS.
"""
import math
import random
from matplotlib import pyplot as plt

try:
	idVal = int(input("Enter your student ID: "))*3
	seed = int(input("Enter seed: "))
	if seed > 3 or seed < 1:
		print ("please use seed of 1, 2, or 3")
		quit()
except:
	print("Please enter as integer")
	quit()

nodes = []
deployments = []
hpas = []
nodeMax = 8 #This value sets the maximum number of nodes. Alter this value to scale your resource pool.
depMax =  3 #This value sets the maximum number of deployments that will be created.
depA = 65 #DO NOT CHANGE THIS VALUE
depB = 65 #DO NOT CHANGE THIS VALUE
commandCount = 1500 #This value determines how many requests will be generated. Alter it to change the duration of your experiment.
separator = " "
expRounds = []
expProg = []
xVals = []
f = open(f"ml_{seed}.txt", "w")
for x in range (1, commandCount+1): #Generates a set number of commands
	commands = [] #Establishes the list of possible commands for this step
	random.seed(idVal+x)
	if len(nodes) == 0:
		cpus = random.randint(5,8)
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
	if len(deployments) == depMax:#If we have deployments
		commands.append("ReqIn")
	if len(hpas)< len(deployments):
		commands.append("CreateHPA")
	choice = random.choice(commands) #Select a command from the pool of available options
	"""
	AddNode creates Node objects that provide the resource pool for deployed pods.
	cpus are the number of cpu resources assigned to a node
	"""
	if choice == "AddNode":
		cpus = random.randint(10,15)
		node = "".join(["Node_",str(len(nodes)+1)])
		command = separator.join([choice, node, str(cpus)])
		f.write(command+"\n")
		nodes.append(node)

	if choice == "Deploy":
		cpus = random.randint(1,3)
		reps = random.randint(1,3)
		depLabel = "".join(map(chr,[depA, depB]))
		if depB < 90:
			depB +=1
		else:
			depA +=1
			depB = 65
		deployment = "".join(["Deployment_",depLabel])
		command = separator.join([choice, deployment, str(reps), str(cpus)])
		f.write(command+"\n")
		deployments.append(deployment)
		if len(expRounds)<len(deployments):
			expRounds.append(1)
			expProg.append(0)

	if choice == "ReqIn":
		if seed == 1:#Generates a stable load 
			newSeed = idVal
			for deployment in deployments:
				random.seed(newSeed)
				reqTime = random.randint(5,15)
				command = separator.join([choice, str(x), deployment, str(reqTime)])
				f.write(command+"\n")
				newSeed +=1

		elif seed == 2:#Generates a load that ramps up to steady level before dropping
			newSeed = idVal
			for deployment in deployments:
				index = deployments.index(deployment)
				random.seed(newSeed*expRounds[index])
				maxTime = random.randint(20,40)
				curMax = random.randint(5, 15)
				if expProg[index] == maxTime:
					expRounds[index] +=1
					expProg[index] = 1
				if expProg[index] > curMax:
					reqTime = curMax
				else:
					reqTime = expProg[index]
				command = separator.join([choice, str(x), deployment, str(reqTime)])
				f.write(command+"\n")
				expProg[index]+=1
				newSeed +=1

		elif seed == 3:#Produces a load in sine pattern
			newSeed = idVal
			for deployment in deployments:
				random.seed(newSeed)
				reqTime = int(random.randint(5,10)*(math.sin(x/random.uniform(10,30))**2))
				command = separator.join([choice, str(x), deployment, str(reqTime)])
				f.write(command+"\n")
				newSeed +=1
	"""
	The following outlines the generation of createHPA commands.
	Supervisory control will run every calibratePeriod*syncPeriod.
	syncPeriod determines the window for hpa metric monitoring.
	calibratePeriod determines how many syncPeriods should pass before the hpa controller is calibrated.
	setPoint is the target utilisation value.
	"""
	if choice == "CreateHPA":
		setPoint = random.randint(60,90)
		syncPeriod = random.randint(5,6)
		calibratePeriod = random.randint(5,8)
		for deployment in deployments:
			if not deployment in hpas:
				command = separator.join([choice, deployment, str(setPoint), str(syncPeriod), str(calibratePeriod)])
				hpas.append(deployment)
				f.write(command+"\n")
				break
			
	f.write("Sleep 1\n")
	
for deployment in deployments:
	f.write ("DeleteDeployment "+deployment+"\n")

