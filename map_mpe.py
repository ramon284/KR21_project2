import pruner
import ordering_func
import marginal_distribution

from BayesNet import BayesNet
import copy
import pandas as pd



def max_out(cpt: pd.DataFrame, var_list:list) -> (pd.DataFrame,tuple):

	cpt = copy.deepcopy(cpt)
	
	prob = cpt.groupby(var_list).aggregate({'p':'max'})
	z = prob.index[0]


	cpt = cpt.drop(columns=var_list)

	rem_vars = [col for col in cpt.columns if col != 'p']

	if len(rem_vars) > 0:

		max_cpt = cpt.groupby(rem_vars).aggregate({'p':'max'})
		max_cpt.reset_index(inplace=True)

	else:
		max_cpt = cpt[cpt.p == cpt.p.max()]

	return max_cpt,z

def sum_out(cpt:pd.DataFrame, var_list:list) -> pd.DataFrame:

	cpt = copy.deepcopy(cpt)

	cpt = cpt.drop(columns = var_list)

	rem_vars = [col for col in cpt.columns if col != 'p']

	if(rem_vars):
		sum_cpt = cpt.groupby(rem_vars).aggregate({'p':'sum'})
	else:
		sum_cpt = pd.DataFrame()
		sum_cpt['p'] = 0
	return sum_cpt

def return_evid_rows(cpt:pd.DataFrame, evidence: dict) -> pd.DataFrame:

	cpt = copy.deepcopy(cpt)
	for var,value in evidence.items():
		if var in cpt.columns:
			cpt = cpt.loc[cpt[var] == value]
	return cpt


def mpe(network:BayesNet, evidence:dict, heuristic:str = 'min-degree') -> (dict,dict):

	network = copy.deepcopy(network)

	pruned_network = pruner.prune_network(network,set(evidence.keys()),{})

	var_list = pruned_network.get_all_variables()

	graph = pruned_network.get_interaction_graph()
	if heuristic == 'min-degree':
		elim_order = ordering_func.sort_min_degree(graph,var_list)
	elif heuristic == 'min-fill':
		elim_order = ordering_func.sort_min_fill(graph,var_list)
	else:
		elim_order = ordering_func.random_sort(var_list)

	cpts_dict = pruned_network.get_all_cpts()

	for var,cpt in cpts_dict.items():
		cpts_dict[var] = return_evid_rows(cpt, evidence)

	z_dict = {}

	for var in elim_order:

		cpts_with_var = marginal_distribution.return_cpts_with_var(cpts_dict, var)
		cpts_list = []
		for key,value in cpts_with_var.items():
			cpts_list.append(value)
		if(len(cpts_list) == 0):
			continue
		prod = cpts_list[0]
		len_cpts_list = len(cpts_list)
		if(len_cpts_list > 1):
			for i in range((len_cpts_list - 1)):
				prod = marginal_distribution.multiply_cpt(prod, cpts_list[i+1])

		prod, z_dict[var] = max_out(prod, [var])

		for key in cpts_with_var.keys():
			cpts_dict.pop(key)
		cpts_dict[' '.join(cpts_with_var.keys())] = prod

	return cpts_dict,z_dict

def map(network:BayesNet, query:set, evidence:dict, heuristic:str = 'min-degree') -> (dict,dict):

	network = copy.deepcopy(network)

	pruned_network = pruner.prune_network(network,set(evidence.keys()),{})

	var_list = pruned_network.get_all_variables()
	#print(var_list)

	graph = pruned_network.get_interaction_graph()
	if heuristic == 'min-degree':
		elim_order = ordering_func.sort_min_degree(graph,var_list)
	elif heuristic == 'min-fill':
		elim_order = ordering_func.sort_min_fill(graph,var_list)
	else:
		elim_order = ordering_func.random_sort(var_list)

	cpts_dict = pruned_network.get_all_cpts()

	for var,cpt in cpts_dict.items():
		cpts_dict[var] = return_evid_rows(cpt, evidence)

	z_dict = {}

	for var in elim_order:

		cpts_with_var = marginal_distribution.return_cpts_with_var(cpts_dict, var)
		cpts_list = []
		for key,value in cpts_with_var.items():
			cpts_list.append(value)
		if(len(cpts_list) == 0):
			continue
		prod = cpts_list[0]
		len_cpts_list = len(cpts_list)
		if(len_cpts_list > 1):
			for i in range((len_cpts_list - 1)):
				prod = marginal_distribution.multiply_cpt(prod, cpts_list[i+1])

		if var in list(query):
			prod, z_dict[var] = max_out(prod, [var])
		else:
			prod = marginal_distribution.summing_var(prod,var)

		for key in cpts_with_var.keys():
			cpts_dict.pop(key)
		cpts_dict[' '.join(cpts_with_var.keys())] = prod

	return cpts_dict,z_dict

