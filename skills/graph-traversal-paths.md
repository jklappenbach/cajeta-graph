---
id: graph-traversal-paths
applies-to: [dev.cajeta.graph.Traversal, dev.cajeta.graph.Components, dev.cajeta.graph.ShortestPaths, dev.cajeta.graph.PathResult, dev.cajeta.graph.DistMatrix]
title: Traversal, components, shortest paths — deterministic orders, explicit unreachability
description: BFS/DFS with contractual visit order, connected/weak/strong components as index-shaped labels (wrong verb for the directedness throws), bfsPath/dijkstra into PathResult (check reachable() before distance()/path()), all-pairs DistMatrix, negative weights refused, and the Θ(n³) allPairsWeighted small-graph warning.
---

# Traversal, components, shortest paths

```cajeta
import dev.cajeta.graph.Traversal;
import dev.cajeta.graph.Components;
import dev.cajeta.graph.ShortestPaths;
import dev.cajeta.graph.PathResult;
import dev.cajeta.graph.DistMatrix;
import cajeta.collection.ArrayList;

ArrayList<String> order = Traversal.bfs(g, "a");   // FIFO, insertion order
int64[] labels = Components.connected(g);          // undirected only
PathResult p = ShortestPaths.dijkstra(g, "a", "g", "weight");
if (p.reachable()) { float64 d = p.distance(); }   // CHECK FIRST
```

## Traversal — order is API

`bfs`/`dfs` visit in edge-insertion neighbour order (DFS = preorder);
repeated runs are identical by contract. Unreachable nodes are omitted;
an unknown source throws.

## Components — pick the verb for the directedness

- `connected(g)` — undirected; a directed graph THROWS (message names
  the right verb).
- `weaklyConnected(g)` / `stronglyConnected(g)` (Kosaraju) — directed;
  undirected throws from strong.
- Labels are index-shaped `int64[]`, ids in discovery order from node
  0; `componentCount(labels)` = max+1.

## Shortest paths — unreachable is an answer

- `bfsPath(g, src, dst)` counts hops; `dijkstra(g, src, dst, attr)`
  sums the NAMED attribute. Negative weights are refused; a missing
  attribute throws (see [[graph-construction]]).
- `PathResult`: `reachable()`, `distance()`, `path()` (source..target,
  a borrow). **`distance()`/`path()` on an unreachable result THROW** —
  there is no infinity in this API. Always branch on `reachable()`.

## All-pairs

- `allPairs(g)` — BFS per node, Θ(n·(n+m)); measured ~2 s at n = 2000
  (docs/scaling.md), but the n² result matrix is the memory wall.
- `allPairsWeighted(g, attr)` — dense-scan Dijkstra per node, **Θ(n³);
  treat as a small-graph tool (n ≲ 500)**.
- `DistMatrix`: `reachableAt(i, j)` then `distAt(i, j)` (throws on an
  unreachable pair). Indexing is node-index order.

Related: [[graph-overview]], [[graph-centrality]] (betweenness rides
the same BFS machinery, with a sampling escape hatch).
