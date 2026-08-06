---
id: graph-overview
applies-to: [dev.cajeta.graph]
title: dev.cajeta.graph — network analysis (the NetworkX role): construction, traversal, centrality, PageRank, Louvain
description: Routing map for dev.cajeta.graph — task → verb table, the string-identity/index-join model every result shares, the all-throws error policy, determinism rules, and the dead-ends (no structural measures, no multigraph, no layout).
---

# dev.cajeta.graph — orientation & routing

Network analysis over the stdlib alone (no estimator protocol, no
drawing). NetworkX 3.6.1 is the parity oracle for construction /
traversal / centrality; python-louvain 0.16 for communities.

## Task → verb

| You want | Use | Skill |
|---|---|---|
| Build a graph (code or Table edge list), typed edges, weights | `Graph` | [[graph-construction]] |
| Visit order, components, shortest paths, all-pairs | `Traversal`, `Components`, `ShortestPaths` | [[graph-traversal-paths]] |
| Who matters: degree/eigenvector/closeness/betweenness, PageRank | `Centrality`, `PageRank` | [[graph-centrality]] |
| Community detection, score a partition | `Louvain`, `Modularity` | [[graph-communities]] |
| Hand structure to chart/LinAlg, join results to identities | `GraphData`, `Graph.toCsr` | [[graph-data-boundary]] |

## The model every result shares

Nodes are `String` at the boundary; inside, each has a contiguous
insertion-order index `0..nodeCount()-1`. **Every algorithm result is
index-shaped** (`float64[]` scores, `int64[]` labels) and joins back
through `g.nodeAt(i)` or `GraphData.nodeIds(g)`. `g.indexOf(id)` is -1
for an unknown id (no throw).

## Package-wide rules

- **No implicit weight.** Weighted verbs take an attribute name; an
  unset attribute THROWS at use — never a silent 1.0.
- **All throws, no warns.** One error type, `GraphException`
  (recoverable). Non-convergence (eigenvector, PageRank) throws and
  does NOT return the last iterate. Zero print sites.
- **Determinism is contractual.** Neighbour order = edge-insertion
  order; BFS/DFS orders are pinned API. All randomness (Louvain visit
  order, betweenness sampling) takes an explicit `uint64` seed
  (Philox) — same seed, bit-identical results, any machine.
- **Simple graphs.** Duplicate `addEdge` UPDATES (no parallel edges);
  self-loops allowed (undirected degree +2).

## Dead-ends (do not hunt)

- No clustering coefficient / diameter / average path length / degree
  distribution (spec §6 minus density did not ship in 0.1.0).
- No multigraph. No layout or drawing — positions belong to
  `dev.cajeta.chart`.
- No Table join-back helper — join by index yourself.
- `Centrality.eigenvector` has NO default `maxIter`/`tol` — pass
  100 / 1e-6 to match NetworkX. (PageRank's defaults ARE built in.)
