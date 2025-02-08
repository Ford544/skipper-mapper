import networkx

from common import read_data

def build_graph_from_file(input_path : str) -> networkx.DiGraph:
    entries = read_data(input_path)
    G = networkx.DiGraph()
    for entry in entries:
        for crosslink in entry["crosslinks"]:
            G.add_edge(entry["name"], crosslink)
    return G

G = build_graph_from_file("data_transformed.jsonl")

#sorted(list(G.in_degree), key=lambda x : x[1], reverse=True)[:10]