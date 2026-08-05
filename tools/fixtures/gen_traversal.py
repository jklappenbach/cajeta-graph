#!/usr/bin/env python3
"""U2 oracle fixture — traversal, components, shortest paths.

Pinned oracle: NetworkX (asserted below). Values are embedded in
src/test/cajeta/dev/cajeta/graph/selftest/TraversalTest.cajeta /
ShortestPathTest.cajeta with provenance comments pointing here.

Run inside the oracle venv:
    ~/code/ml/venv-graph-ref/bin/python tools/fixtures/gen_traversal.py
"""
import networkx as nx

assert nx.__version__ == "3.6.1", nx.__version__

# --- weighted graph for Dijkstra (undirected), hand-drawable ------------
#        a --1-- b --2-- c
#        |       |       |
#        4       7       3
#        |       |       |
#        d --1-- e --1-- f
# plus f --9-- g,  c --1-- g,  h isolated
WEDGES = [
    ("a", "b", 1.0), ("b", "c", 2.0), ("a", "d", 4.0), ("b", "e", 7.0),
    ("c", "f", 3.0), ("d", "e", 1.0), ("e", "f", 1.0), ("f", "g", 9.0),
    ("c", "g", 1.0),
]

G = nx.Graph()
for u, v, w in WEDGES:
    G.add_edge(u, v, weight=w)
G.add_node("h")

print("== dijkstra a->g (weighted) ==")
d = nx.dijkstra_path_length(G, "a", "g", weight="weight")
p = nx.dijkstra_path(G, "a", "g", weight="weight")
print("dist:", d, "path:", p)

print("== bfs shortest path a->g (unweighted) ==")
print("hops:", nx.shortest_path_length(G, "a", "g"),
      "path:", nx.shortest_path(G, "a", "g"))

print("== unreachable ==")
print("a->h has path:", nx.has_path(G, "a", "h"))

print("== all-pairs unweighted on the same graph ==")
ap = dict(nx.all_pairs_shortest_path_length(G))
order = sorted(G.nodes())
for u in order:
    row = [ap[u].get(v, None) for v in order]
    print(u, row)

print("== all-pairs weighted (dijkstra) a-row ==")
apw = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
print("a", [round(apw["a"].get(v, float("nan")), 6) for v in order])

# --- components ---------------------------------------------------------
print("== undirected components ==")
H = nx.Graph()
H.add_edges_from([("a", "b"), ("b", "c"), ("d", "e")])
H.add_node("f")
print(sorted(sorted(c) for c in nx.connected_components(H)))

print("== directed weak/strong ==")
D = nx.DiGraph()
# cycle x->y->z->x, tail z->w, isolated v; extra edge w->q
D.add_edges_from([("x", "y"), ("y", "z"), ("z", "x"), ("z", "w"), ("w", "q")])
D.add_node("v")
print("weak:", sorted(sorted(c) for c in nx.weakly_connected_components(D)))
print("strong:", sorted(sorted(c) for c in nx.strongly_connected_components(D)))
