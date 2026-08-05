#!/usr/bin/env python3
"""U4 oracle fixture — modularity + Louvain community detection.

Pinned oracles: NetworkX (modularity) and python-louvain (best_partition),
both asserted below. python-louvain is single-purpose and lightly
maintained (spec §1.3): divergence from it is a finding to investigate,
not automatically a bug. Values are embedded in
src/test/cajeta/dev/cajeta/graph/selftest/LouvainTest.cajeta.

Run inside the oracle venv:
    ~/code/ml/venv-graph-ref/bin/python tools/fixtures/gen_louvain.py
"""
import community as community_louvain
import networkx as nx

assert nx.__version__ == "3.6.1", nx.__version__
assert community_louvain.__version__ == "0.16", community_louvain.__version__


def clique(g, names, w=None):
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if w is None:
                g.add_edge(names[i], names[j])
            else:
                g.add_edge(names[i], names[j], weight=w)


# --- barbell: two 5-cliques joined by one edge --------------------------
B = nx.Graph()
A = [f"a{i}" for i in range(5)]
Bn = [f"b{i}" for i in range(5)]
clique(B, A)
clique(B, Bn)
B.add_edge("a0", "b0")

known = [set(A), set(Bn)]
print("== barbell: modularity of the two-clique partition ==")
print(round(nx.community.modularity(B, known), 10))

print("== barbell: python-louvain best_partition (seeded) ==")
part = community_louvain.best_partition(B, random_state=7)
groups = {}
for n, c in part.items():
    groups.setdefault(c, set()).add(n)
print(sorted(sorted(g) for g in groups.values()))
print("modularity:", round(community_louvain.modularity(part, B), 10))

# --- chain of three triangles (resolution direction) --------------------
T = nx.Graph()
clique(T, ["a1", "a2", "a3"])
clique(T, ["b1", "b2", "b3"])
clique(T, ["c1", "c2", "c3"])
T.add_edge("a3", "b1")
T.add_edge("b3", "c1")

print("== triangles: known 3-community modularity ==")
kt = [{"a1", "a2", "a3"}, {"b1", "b2", "b3"}, {"c1", "c2", "c3"}]
print(round(nx.community.modularity(T, kt), 10))

for res in (0.05, 1.0):
    part = community_louvain.best_partition(T, resolution=res,
                                            random_state=7)
    print(f"res {res}: communities = {len(set(part.values()))}")

# --- weighted pair of triangles -----------------------------------------
W = nx.Graph()
clique(W, ["p1", "p2", "p3"], w=5.0)
clique(W, ["q1", "q2", "q3"], w=5.0)
W.add_edge("p1", "q1", weight=0.5)
kw = [{"p1", "p2", "p3"}, {"q1", "q2", "q3"}]
print("== weighted triangles: modularity of the two-triangle partition ==")
print(round(nx.community.modularity(W, kw, weight="weight"), 10))

# resolution: standard modularity at gamma=1 reproduced by resolution=1
print("== triangles: nx modularity at resolution 1 equals default ==")
print(nx.community.modularity(T, kt) ==
      nx.community.modularity(T, kt, resolution=1))
