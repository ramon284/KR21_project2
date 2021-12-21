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

	summed_cpt = pd.concat([true_rows, false_rows]).groupby(cols, as_index=False)["p"].sum()
	return summed_cpt

def multiply_cpt(cpt1: pd.DataFrame, cpt2: pd.DataFrame) -> pd.DataFrame:

	cpt1_copy = copy.deepcopy(cpt1)
	cpt2_copy = copy.deepcopy(cpt2)

	col1 = []
	for col in cpt1_copy.columns:
		if col != 'p':
			col1.append(col)

	col2 = []
	for col in cpt2_copy.columns:
		if col != 'p':
			col2.append(col)

	common_vars = []

	if len(col1)>len(col2):
		for col in col2:
			if col in col1:
				common_vars.append(col)
	else:
		for col in col1:
			if col in col2:
				common_vars.append(col)
	
	merged_cpts = pd.merge(cpt1_copy, cpt2_copy, on=common_vars)
	merged_cpts['p'] = merged_cpts['p_x'] * merged_cpts['p_y']
	merged_cpts.drop(['p_x', 'p_y'], inplace=True, axis=1)

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

def marginal_distribution(network: BayesNet, query:set, evidence:dict, heuristic:str="min-fill") -> pd.DataFrame:
	bn_var_list = network.get_all_variables()
	diff_var_list = list(set(bn_var_list) - query)

	if(heuristic=="random"):
		#print("heuristic used : random")
		o_diff_var_list = ordering.random_sort(diff_var_list)
	elif(heuristic=="min-degree"):
		#print("heuristic used : min-degree")
		o_diff_var_list = ordering.sort_min_degree(network.get_interaction_graph(),diff_var_list)
	else:
		#print("heuristic used : min-fill")
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
		prod = cpts_list[0]
		for i in range(len(cpts_with_var) - 1):
			prod = multiply_cpt(prod, cpts_list[i+1])
		prod_sum = summing_var(prod,var)
		for variable,cpt in cpts_with_var.items():
			del all_cpts[variable]
		all_cpts[str(i)] = prod_sum
		i+=1

	all_cpts_list = list(all_cpts.values())

	marginalised_cpt = all_cpts_list[0]

	for i in range(len(all_cpts_list) - 1):
		marginalised_cpt = multiply_cpt(marginalised_cpt,all_cpts_list[i+1])

	if evidence:
		evidence_vars_cpt = marginal_distribution(network,set(evidence.keys()),{},'random')
		for var, evidence_bool in evidence.items():
			evidence_vars_cpt = evidence_vars_cpt[evidence_vars_cpt[var] == evidence_bool]

		evidence_prob = evidence_vars_cpt.iloc[0]['p']

	else:
		evidence_prob = 1

	marginalised_cpt['p'] /= evidence_prob
	return marginalised_cpt



