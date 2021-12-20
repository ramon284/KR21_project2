from typing import Union
from BayesNet import BayesNet
import ordering_func
import dsep
import copy
import pruner
import marginal_distribution

class BNReasoner:
    def __init__(self, net: Union[str, BayesNet]):
        """
        :param net: either file path of the bayesian network in BIFXML format or BayesNet object
        """
        if type(net) == str:
            # constructs a BN object
            self.bn = BayesNet()
            # Loads the BN from an BIFXML file
            self.bn.load_from_bifxml(net)
        else:
            self.bn = net
        
    def dSeperator(self, network : BayesNet, x: set ,z: set ,y: set) -> bool:
        tempCopy = copy.deepcopy(network) ##to prevent pruning the original network
        return dsep.check_dseperated(tempCopy,x,z,y)
    
    def ordering(self, network: BayesNet, x:list, order_type:str) -> list:
        ## order x based on min-fill and min-degree heuristics
        output = None
        if (order_type == 'random'):
            output = ordering_func.random_sort(x)
        elif (order_type == 'min-degree'):
            graph = network.get_interaction_graph()
            output = ordering_func.sort_min_degree(graph,x)
        else:
            graph = network.get_interaction_graph()
            output = ordering_func.sort_min_fill(graph,x)
        
        return output
    
    def networkPruning(self, network: BayesNet, evidence: set, query: set) -> BayesNet: 
        ## set of variables Q and evidence E
        pruned_network = copy.deepcopy(network)
        pruner.prune_network(pruned_network, evidence, query)
        return pruned_network
    
    def marginalDistributions(self, network, q, e, heuristic):
        network_copy = copy.deepcopy(network)
        return marginal_distribution.marginal_distribution(network_copy,q,e,heuristic)
    
    def MAP(self, network, q, e):
        return
    
    def MPE(self, network, q, e):
        return

    # TODO: This is where your methods should go

#filePath = 'testing/dog_problem.BIFXML' ## filepath
#bnet = BNReasoner(filePath) ## make empty network
#x, z, y = {"light-on"}, {"family-out"}, {"dog-out"}
#bnet.bn.draw_structure() ## draw the graph
#print(bnet.dSeperator(bnet, x,z,y))
#bnet.draw_structure() ## draw the graph