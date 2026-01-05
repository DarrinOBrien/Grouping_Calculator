# Based on adjacency list as adjacency matrix would introduce unhelpful overhead
class Node():
    def __init__(self, indice, val, neighbors=None):
        self.node_indice = indice
        self.val = val
        self.neighbors = neighbors if neighbors is not None else {}
    
    def add_neighbor(self, node_indice, edge_weight=1):
        self.neighbors[node_indice] = edge_weight
    
    def remove_neighbors(self, node_indice):
        try:
            del self.node_indice[node_indice]
        except KeyError:
            print(f"Key {node_indice} was not found")
    
    def update_edge_weight(self, node_indice, new_edge_weight):
        self.neighbors[node_indice] = new_edge_weight
    
    def get_node_indice(self):
        return self.node_indice
    
    def get_val(self):
        return self.val

    def get_neighbors(self):
        return self.neighbors
    
    def get_neighbors_indices(self):
        return list(self.neighbors.keys())
    
    def __repr__(self):
        return f"{self.val}: {self.neighbors}"

class AdjacencyList():
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes is not None else []
        self.curr_indice = len(nodes)-1 if self.nodes else 0
    
    def add_node(self, val):
        self.nodes.append(Node(self.curr_indice, val))
        self.curr_indice += 1
    
    def get_node(self, indice):
        return self.nodes[indice]
    
    def get_nodes(self):
        return self.nodes
    
    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        repr = {}
        for i in range(len(self.nodes)):
            repr[i] = self.get_node(i).get_neighbors_indices()
        return f"{repr}"
            
def create_graph(sample):
    adjacency_list = AdjacencyList()
    for equation in sample["full_equations"]:
        adjacency_list.add_node(equation)
    
    # Helpful debug info for full structures
    # for samp, val in sample.items():
    #     print(samp, val)
    # print()
    
    for i in range(len(adjacency_list)):
        for j in range(len(adjacency_list)):
            neighbors = set(adjacency_list.get_node(i).get_neighbors_indices())
            if i == j or sample["solutions"][i] == sample["solutions"][j] or j in neighbors: # If a number is redefined, ignore the case
                continue

            if sample["solutions"][i] in sample["operands"][j]:
                if sample["solutions"][i] in sample["main_operands"][j]:
                    adjacency_list.get_node(i).add_neighbor(j, 1.0)
            elif sample["is_single_func"][i]:
                if sample["expressions"][i] in sample["expressions"][j] or sample["solutions"][i] in sample["expressions"][j]:
                    adjacency_list.get_node(i).add_neighbor(j, 1.0)
            elif sample["has_sub_expressions"][j]:
                for sub_express_result in sample["sub_expression_results"][j]:
                    if float(sample["solutions"][i]) == float(sub_express_result):
                        adjacency_list.get_node(i).add_neighbor(j, 1.0)
    
    return adjacency_list