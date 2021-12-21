import os
import itertools as it
import BNReasoner as bn
import time as t
import pandas as pd
import random

directory = 'testing/'
methods = ['MPE', 'MAP', 'marginal']
heuristics = ['min-degree', 'min-fill', 'random'] ## for map and mpe

bifxmlList = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if(filename.endswith('.BIFXML')):
        bifxmlList.append(directory+filename)
        
print(bifxmlList) ## contains the path to all of our test cases



for method in methods: ##TODO## turn e into a dict here for it to work
    for heuristic in heuristics:
        time = []
        variableSize = []
        for file in bifxmlList:
            network = bn.BNReasoner(file) ## make network
            variables = network.bn.get_all_variables()
            x = list(range(1, len(variables)))
            x2, vars = zip(*random.sample(list(zip(x, variables)), 2))
            e, q = vars[0], vars[1] ## sample 2 random variables from the list
            if(method == 'MPE'):
                startTime = t.time()
                network.MPE(network=network, q=set([q]), e=e ,heuristic=heuristic)
                endTime = t.time() - startTime
                time.append(endTime)
                variableSize.append(len(variables))
            elif(method == 'MAP'):
                startTime = t.time()
                network.MPE(network=network, q=set([q]), e=e ,heuristic=heuristic)
                endTime = t.time() - startTime
                time.append(endTime)
                variableSize.append(len(variables))
            elif(method == 'marginal'):
                startTime = t.time()
                network.marginalDistributions(network=network, q=set([q]), e=e ,heuristic=heuristic)
                endTime = t.time() - startTime
                time.append(endTime)
                variableSize.append(len(variables)) 
        
        excel = pd.dataFrame({
            'variableSize':len(variables),
            'time':endTime
        })
        excel.to_csv('gathered_data/'+method+'-'+heuristic+'.csv')
        time = []
        variableSize = []


#reasoner = BR('testing/dog_problem.bifxml')
#heuristics = ['min-degree', 'min-fill', 'random_sort']
#methods = ['MPE', 'MAP', 'marginal']

#possibilities = list(it.product(heuristics, methods))

#temp = []
#for heuristic, method in possibilities:
#    temp.append(heuristic + " " + method)


