import copy
import pandas as pd

import ordering_func as ordering
from BayesNet import BayesNet


def summing_var(cpt: pd.DataFrame, var: str) -> pd.DataFrame:

	cpt_copy = copy.deepcopy(cpt)
	var_mask = cpt_copy[var]

	true_rows = cpt_copy[var_mask].drop(var, axis=1)
	false_rows = cpt_copy[~var_mask].drop(var,axis=1)

	cols=[]

	for col in true_rows.columns:
		if col != 'p':
			cols.append(col)

	if(cols):
		summed_cpt = pd.concat([true_rows, false_rows]).groupby(cols, as_index=False)["p"].sum()
	else:
		summed_cpt = pd.DataFrame()
		summed_cpt['p'] = 0
	return summed_cpt

def multiply_cpt(cpt1: pd.DataFrame, cpt2: pd.DataFrame) -> pd.DataFrame:

	cpt1_copy = copy.deepcopy(cpt1)
	cpt2_copy = copy.deepcopy(cpt2)

	col1 = [col for col in cpt1_copy.columns if col != 'p']
	col2 = [col for col in cpt2_copy.columns if col != 'p']
	common_vars = list(set(col1).intersection(set(col2)))
	
	if(common_vars):
		merged_cpts = pd.merge(cpt1_copy, cpt2_copy, on=common_vars)
		merged_cpts['p'] = merged_cpts['p_x'] * merged_cpts['p_y']
		merged_cpts.drop(['p_x', 'p_y'], inplace=True, axis=1)

	else:
		print("Program bugged. Results may be incorrect.")
		cpt1_copy['temp'] = 1
		cpt2_copy['temp'] = 1
		merged_cpts = pd.merge(cpt1_copy, cpt2_copy, on=['temp'])
		merged_cpts['p'] = 1.0
		merged_cpts.drop(['p_x', 'p_y', 'temp'], inplace=True, axis=1)		

	return merged_cpts

def return_cpts_with_var(cpt_dict: dict, var:str) -> dict:
	cpt_dict_var = {}

	for variable,cpt in cpt_dict.items():
		if var in cpt.columns:
			cpt_dict_var[variable] = cpt

	return cpt_dict_var

def remove_evidence_rows(cpt: pd.DataFrame, evidence:dict) -> pd.DataFrame:
	cpt_copy = copy.deepcopy(cpt)
	for evidence_var, evidence_bool in evidence.items():
		if evidence_var in cpt_copy.columns:
			cpt_copy.loc[cpt_copy[evidence_var] != evidence_bool, 'p'] = 0

	return cpt_copy

def marginal_distribution(network: BayesNet, query:set, evidence:dict, heuristic:str='min-degree') -> pd.DataFrame:
	network = copy.deepcopy(network)
	bn_var_list = network.get_all_variables()
	diff_var_list = list(set(bn_var_list) - query)

	if(heuristic=="random"):
		o_diff_var_list = ordering.random_sort(diff_var_list)
	elif(heuristic=="min-degree"):
		o_diff_var_list = ordering.sort_min_degree(network.get_interaction_graph(),diff_var_list)
	else:
		o_diff_var_list = ordering.sort_min_fill(network.get_interaction_graph(), diff_var_list)

	all_cpts = network.get_all_cpts()

	for var, cpt in all_cpts.items():
		all_cpts[var] = remove_evidence_rows(cpt,evidence)

	i=0

	for var in o_diff_var_list:
		cpts_with_var = return_cpts_with_var(all_cpts, var)
		cpts_list = []
		for key,value in cpts_with_var.items():
			cpts_list.append(value)
		if(len(cpts_list) == 0):
			continue
		prod = cpts_list[0]
		len_cpts_list = len(cpts_list)
		if(len_cpts_list > 1):
			for i in range((len_cpts_list - 1)):
				prod = multiply_cpt(prod, cpts_list[i+1])
		prod_sum = summing_var(prod,var)
		for variable,cpt in cpts_with_var.items():
			del all_cpts[variable]
		all_cpts[str(i)] = prod_sum
		i+=1

	all_cpts_list = list(all_cpts.values())

	marginalised_cpt = all_cpts_list[0]

	len_all_cpts_list = len(all_cpts_list)
	if(len_all_cpts_list>1):
		for i in range((len_all_cpts_list - 1)):
			marginalised_cpt = multiply_cpt(marginalised_cpt,all_cpts_list[i+1])

	if evidence:
		set_evidence_keys = set(evidence.keys())
		evidence_vars_cpt = marginal_distribution(network,set_evidence_keys,{})
		for var, evidence_bool in evidence.items():
			evidence_vars_cpt = evidence_vars_cpt[evidence_vars_cpt[var] == evidence_bool]
		evidence_prob = evidence_vars_cpt.iloc[0]['p']

	else:
		evidence_prob = 1.0
		
	marginalised_cpt['p'] /= evidence_prob
	return marginalised_cpt



