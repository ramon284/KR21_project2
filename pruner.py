import copy
from BayesNet import BayesNet

def prune(network: BayesNet, evidence: set, query: set) -> None: 
    leaf_nodes = get_leaves(network) ## get the leaves
    nodes = evidence.union(query)    ## all the nodes in our E and Q
    for leaf in leaf_nodes:
        if leaf not in nodes:        ## remove leaf that's not in E and Q
            network.del_var(leaf)

def prune_edges(network: BayesNet, evidence: set) -> None:
    for node in evidence:
        edges = [] 
        for u, v in network.structure.edges(nbunch=evidence):
            edges.append(v)
        for edge in edges:
            network.del_edge((node, edge))

def get_leaves(network: BayesNet) -> list:
    leaves = [] 
    nodes = set(network.get_all_variables())
    for node in nodes: 
        if len(network.get_children(node)) == 0:
            leaves.append(node) 
    return leaves

def prune_network(network: BayesNet, evidence: set, query: set) -> None:
    prune(network, evidence, query)
    prune_edges(network, evidence)



#bnet = BayesNet() ## make empty network
#bnet.load_from_bifxml(file_path='testing/lecture_example2.BIFXML') ## fill that bitch up with data
#bnetBefore = copy.deepcopy(bnet)
#print(bnet.get_all_variables())
#prune_network(bnet, evidence, query)
#print(bnet.get_all_variables())
