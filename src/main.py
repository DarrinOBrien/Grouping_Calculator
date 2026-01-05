from parser import process_dataset, combine_dicts
from structures import create_graph
from logic import classify_groups, sort_groups, chain_groups, print_chain

if __name__ == "__main__":
    train, test = process_dataset("./data")
    combined_dict = combine_dicts([train[57], train[58]])
    adjacency_list = create_graph(combined_dict)
    all_groups, reverse_adjacency = classify_groups(adjacency_list)
    ordering = sort_groups(all_groups, adjacency_list, reverse_adjacency)
    chained_groups = chain_groups(all_groups, adjacency_list, reverse_adjacency)
    for chain in chained_groups:
        print_chain(chain, adjacency_list)
    
    '''
    for i, node in enumerate(adjacency_list.get_nodes()):
        print(f"{i}: {node}")
    
    print(f"All Groups: {all_groups}")
    print(f"Adjacency List: {adjacency_list}")
    print(f"Reverse Adjacency: {reverse_adjacency}")

    print(f"Ordering: {ordering}")

    print(chained_groups)
    '''