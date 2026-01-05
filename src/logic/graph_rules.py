from collections import defaultdict

def classify_groups(adjacency_list):
    visited = set()
    all_groups = []

    node_list = adjacency_list.get_nodes()

    reverse_adjacency = defaultdict(list)
    for i in range(len(node_list)):
        for neighbor_indice in adjacency_list.get_node(i).get_neighbors_indices():
            reverse_adjacency[neighbor_indice].append(i)

    for i in range(len(node_list)):
        if i not in visited:
            current_group = []
            queue = [i]

            while len(queue) > 0:
                current = queue.pop(0)

                if current in visited:
                    continue

                visited.add(current)
                current_group.append(current)

                neighbors = set(adjacency_list.get_node(current).get_neighbors_indices()).union(reverse_adjacency[current])

                for neighbor_indice in neighbors:
                    if neighbor_indice not in visited:
                        queue.append(neighbor_indice)
            
            all_groups.append(current_group)
    
    return all_groups, reverse_adjacency

def sort_groups(all_groups, adjacency_list, reverse_adjacency):
    # Kahn's Algorithm
    possible_combos = []

    for group in all_groups:
        in_degree = {}
        for node_indice in group:
            in_degree[node_indice] = len(reverse_adjacency[(node_indice)])

        queue = []
        for i, num_in in in_degree.items():
            if num_in == 0:
                queue.append(i)
        
        ordering = []
        while queue:
            node_indice = queue.pop(0)
            ordering.append(node_indice)

            for neighbor_indice in adjacency_list.get_node(node_indice).get_neighbors_indices():
                in_degree[neighbor_indice] -= 1
                if in_degree[neighbor_indice] == 0:
                    queue.append(neighbor_indice)
        
        possible_combos.append(ordering)
    
    return possible_combos

def chain_groups(all_groups, adjacency_list, reverse_adjacency): 
    chained_representations = []

    for group in all_groups:
        terminal_node = 0
        seen = set()
        for node_indice in group:
            if not adjacency_list.get_node(node_indice).get_neighbors_indices():
                terminal_node = node_indice
                seen.add(terminal_node)
                break

        def build_chain(node, reverse_adjacency):
            return {
                node: [
                    build_chain(parent, reverse_adjacency) for parent in reverse_adjacency[node]
                ]
            }
        
        chain = build_chain(terminal_node, reverse_adjacency)
        chained_representations.append(chain)
    
    return chained_representations

def print_chain(chained_group, adjacency_list):
    def print_seg(part, num_tabs):
        for dict in part:
            for key, values in dict.items():
                print(f"{num_tabs * '\t'}{key}: {adjacency_list.get_node(key).get_val()}")
                if values:
                    print_seg(values, num_tabs=num_tabs+1)
    
    for key, _ in chained_group.items():
        print(f"{key}: {adjacency_list.get_node(key).get_val()}")
        print_seg(chained_group[key], num_tabs=1)