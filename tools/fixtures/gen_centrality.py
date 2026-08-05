#!/usr/bin/env python3
"""U3 oracle fixture — centrality family + PageRank.

Pinned oracle: NetworkX (asserted below). Values are embedded in
src/test/cajeta/dev/cajeta/graph/selftest/CentralityTest.cajeta /
PageRankTest.cajeta with provenance comments pointing here.

Run inside the oracle venv:
    ~/code/ml/venv-graph-ref/bin/python tools/fixtures/gen_centrality.py
"""
import networkx as nx

assert nx.__version__ == "3.6.1", nx.__version__


def show(tag, d, nodes):
    print(tag, [round(d[n], 10) for n in nodes])


# --- hand-checkable star (spec 9.2): center s, leaves l1..l4 ------------
S = nx.Graph()
for i in range(1, 5):
    S.add_edge("s", f"l{i}")
SN = ["s", "l1", "l2", "l3", "l4"]
print("== star: degree ==")
show("deg", nx.degree_centrality(S), SN)
print("== star: betweenness (normalized) ==")
show("btw", nx.betweenness_centrality(S), SN)
print("== star: betweenness (raw) ==")
show("btwraw", nx.betweenness_centrality(S, normalized=False), SN)
print("== star: closeness ==")
show("clo", nx.closeness_centrality(S), SN)
print("== star: eigenvector (maxIter 100 tol 1e-6) ==")
show("eig", nx.eigenvector_centrality(S, max_iter=100, tol=1e-6), SN)

# --- the U2 fixture graph a..g (+ h isolated) ---------------------------
WEDGES = [
    ("a", "b", 1.0), ("b", "c", 2.0), ("a", "d", 4.0), ("b", "e", 7.0),
    ("c", "f", 3.0), ("d", "e", 1.0), ("e", "f", 1.0), ("f", "g", 9.0),
    ("c", "g", 1.0),
]
G = nx.Graph()
for u, v, w in WEDGES:
    G.add_edge(u, v, weight=w)
GN = list("abcdefg")

print("== G: eigenvector unweighted ==")
show("eig", nx.eigenvector_centrality(G, max_iter=100, tol=1e-6), GN)
print("== G: eigenvector weighted ==")
show("eigw", nx.eigenvector_centrality(G, max_iter=100, tol=1e-6,
                                       weight="weight"), GN)
print("== G: betweenness normalized ==")
show("btw", nx.betweenness_centrality(G), GN)
print("== G: betweenness endpoints ==")
show("btwe", nx.betweenness_centrality(G, endpoints=True), GN)

Gh = G.copy()
Gh.add_node("h")
GHN = list("abcdefgh")
print("== G+h: closeness (disconnected convention) ==")
show("clo", nx.closeness_centrality(Gh), GHN)

print("== G: sampled betweenness k=n equals exact ==")
exact = nx.betweenness_centrality(G)
samp = nx.betweenness_centrality(G, k=len(G), seed=7)
print("max|k=n - exact|:", max(abs(exact[n] - samp[n]) for n in GN))

# --- eigenvector non-convergence: a budget too small to converge -------
# (The x + Ax shift damps bipartite oscillation, so the classic 4-cycle
# DOES converge; the reliable trigger is an unmeetable budget.)
try:
    nx.eigenvector_centrality(G, max_iter=2, tol=1e-12)
    print("== nonconvergence: UNEXPECTED SUCCESS ==")
except nx.PowerIterationFailedConvergence:
    print("== nonconvergence: NetworkX raises PowerIterationFailedConvergence ==")

# --- directed dependency graph with a rank sink -------------------------
# app->lib1, app->lib2, tool->lib2, lib1->util, lib2->util; util imports
# nothing (the leaf-utility sink §4.4.2).
D = nx.DiGraph()
D.add_edges_from([("app", "lib1"), ("app", "lib2"), ("tool", "lib2"),
                  ("lib1", "util"), ("lib2", "util")])
DN = ["app", "lib1", "lib2", "tool", "util"]

print("== dep: in/out degree centrality ==")
show("in", nx.in_degree_centrality(D), DN)
show("out", nx.out_degree_centrality(D), DN)

print("== dep: pagerank damping 0.85 ==")
show("pr", nx.pagerank(D, alpha=0.85, max_iter=100, tol=1e-6), DN)
print("sum:", sum(nx.pagerank(D, alpha=0.85).values()))

print("== dep: pagerank on reverse ==")
show("prR", nx.pagerank(D.reverse(), alpha=0.85, max_iter=100, tol=1e-6), DN)

print("== dep: personalized (all mass on app) ==")
p = {n: (1.0 if n == "app" else 0.0) for n in D}
show("prP", nx.pagerank(D, alpha=0.85, personalization=p,
                        max_iter=100, tol=1e-6), DN)

print("== dep weighted: lib2 edge heavier ==")
DW = nx.DiGraph()
DW.add_edge("app", "lib1", w=1.0)
DW.add_edge("app", "lib2", w=3.0)
DW.add_edge("tool", "lib2", w=1.0)
DW.add_edge("lib1", "util", w=1.0)
DW.add_edge("lib2", "util", w=1.0)
show("prW", nx.pagerank(DW, alpha=0.85, weight="w",
                        max_iter=100, tol=1e-6), DN)

# --- directed betweenness on the dep graph ------------------------------
print("== dep: betweenness normalized (directed) ==")
show("btwD", nx.betweenness_centrality(D), DN)
