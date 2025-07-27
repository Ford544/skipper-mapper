import networkx as nx


from common import read_data

def build_graph_from_file(input_path : str) -> nx.DiGraph:
    entries = read_data(input_path)
    G = nx.DiGraph()
    nodes = {entry["name"] : entry for entry in entries}
    for entry in entries:
        for crosslink in entry["crosslinks"]:
            G.add_edge(entry["name"], crosslink)
    nx.set_node_attributes(G, nodes)
    return G

def list_to_gexf(l : list):
    return "[" + ", ".join(l) + "]"

def stringify_list_attrs(G):
    nx.set_node_attributes(G, {node : {key : list_to_gexf(value) if type(value) == list else value for key, value in attrs.items()} for node, attrs in G.nodes.items()})

G = build_graph_from_file("data_transformed.jsonl")
stringify_list_attrs(G)

nx.write_gexf(G, "skipper.graphml")
#sorted(list(G.in_degree), key=lambda x : x[1], reverse=True)[:10]