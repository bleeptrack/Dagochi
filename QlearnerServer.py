from mdp import *
from maploader import *
import random, pickle, copy, time

#Hyperparameters
totalEpisodes = 100
maxRolloutLength = 100
learningRate = 0.1
discountFactor = 0.95
epsilon = 0.85
epsilonDecay = 0.01
random.seed(1)

actions = ["r", "l", "u", "d"]
qTable = {}#state->actions->values

if os.path.exists("./qTable.pickle"):
	currEngine = pickle.load(open("qTable.pickle", "rb"))

while True:
	time.sleep(3)
	print (" ")
	envs = GrabEnvironments()
	currEnv = random.choice(envs)
	print ("Dagochi: playing "+str(currEnv.mapName)+"!")
	SARs = []
	rolloutComplete = False
	rolloutIndex = 0
	totalReward = 0

	while rolloutIndex < maxRolloutLength and not rolloutComplete:
		rolloutIndex+=1

		state = State(currEnv)

		#Action Selection
		action = random.choice(actions)
		if state.state in qTable.keys():
			maxAction = action
			maxValue = -1000

			for a in actions:
				if a in qTable[state.state].keys():
					if maxValue < qTable[state.state][a]:
						maxValue = qTable[state.state][a]
						maxAction = a
			action = maxAction
		else:
			action = random.choice(actions)


		if random.random()>epsilon:
			action = random.choice(actions)
		if epsilon<1:
			epsilon+=epsilonDecay


		#s_(t+1) <- s_t
		nextEnvironment = currEnv.child()

		if action=="r":
			nextEnvironment = MoveRight(nextEnvironment)
		elif action =="l":
			nextEnvironment = MoveLeft(nextEnvironment)
		elif action =="u":
			nextEnvironment = MoveUp(nextEnvironment)
		elif action =="d":
			nextEnvironment = MoveDown(nextEnvironment)

		reward = CalculateReward(currEnv, nextEnvironment)
		totalReward+=reward

		SARs.append([state.state, action, reward])
		currEnv = nextEnvironment

		#Check if complete
		if len(currEnv.playerPos)==0 or currEnv.totalCrystals==currEnv.collectedCrystals:
			rolloutComplete = True

	#print ("Episode: "+str(i)+" total reward: "+str(totalReward))

	# Q-update
	for j in range(len(SARs)-1, 0, -1):
		oldQValue = 0#assume 0 initialization
		optimalFutureValue = -10

		if SARs[j][0] in qTable.keys():
			if SARs[j][1] in qTable[SARs[j][0]].keys():
				oldQValue = qTable[SARs[j][0]][SARs[j][1]]

			if j+1<len(SARs)-1:
				for a in actions:
					if a in qTable[SARs[j+1][0]].keys():
						if optimalFutureValue < qTable[SARs[j+1][0]][a]:
							optimalFutureValue = qTable[SARs[j+1][0]][a]
			else:
				optimalFutureValue = 0

		newQValue = oldQValue + learningRate*(SARs[j][2] + discountFactor*optimalFutureValue - oldQValue)

		if not SARs[j][0] in qTable.keys():
			qTable[SARs[j][0]] = {}
		qTable[SARs[j][0]][SARs[j][1]] = newQValue


	qTableSum = 0
	for keys in qTable.keys():
		for keys2 in qTable[keys].keys():
			qTableSum += qTable[keys][keys2]


	#print ("Q table sum: "+ ("%0.2f" %qTableSum))
	print ("--- Total Reward: "+str(totalReward)+". Total Lifetime: "+str(rolloutIndex)+"% ---")

	mood = qTableSum

	depressed = False

	if mood < -500:
		depressed = True

	if not depressed:
		if totalReward<-100:
			print ("Dagochi: ε(´סּ︵סּ`)з")
			print ("Dagochi: Oh I didn't do very well, but I'll get better!")
		if totalReward<=100 and totalReward>=-100:
			print ("Dagochi: ¯\\(°_o)/¯")
			print ("Dagochi: Well, at least I'm not dead!")
		if totalReward>100:
			print ("Dagochi: ᕕ( ᐛ )ᕗ")
			print ("Dagochi: Oh wow I did great!")
	else:
		if totalReward<0: 
			print ("Dagochi: (︶︹︶)")
			print ("Dagochi: Of course it went badly.")
		if totalReward>=0:
			print ("Dagochi: (ﾉ◕ヮ◕)ﾉ")
			print ("Dagochi: Whoa! That was fun!")
		

	pickle.dump(qTable,open("qTable.pickle", "wb"))



