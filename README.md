# cajeta-graph

Network analysis for the cajeta ecosystem: `dev.cajeta.graph`. Graphs
with string identities and typed edges, deterministic traversal,
connectivity, shortest paths, the centrality family with PageRank, and
Louvain community detection with modularity.

Graph analytics is not machine learning — nothing here uses the
estimator protocol — so the library depends on the stdlib alone. It also
draws nothing: structure is emitted as plain data for `dev.cajeta.chart`
to render.

## Documentation

| Page | What it covers |
|---|---|
| [Documentation index](docs/README.md) | Orientation and quick start |
| [Guide](docs/Guide.md) | The graph type, every algorithm, API shapes, error policy |
| [Tour](docs/Tour.md) | The runnable, self-checking walkthrough — 14 sections, `cajeta tour` |
| [Differences from NetworkX](docs/DifferencesFromNetworkX.md) | Deliberate divergences, plus what is honestly not implemented |
| [Scaling](docs/scaling.md) | Measured betweenness/all-pairs numbers and the recommendations they support |

Agent-facing **skills** ship inside the `.cja` (`skills/*.md`, indexed):
`cajeta search-skill dev.cajeta.graph` / `list-skills` / `get-skills`
route a coding agent to the right verb and the hazards — start at
`graph-overview`.

## Quick start

```cajeta
Graph g = Graph.undirected();
g.addEdge("a", "b");
g.setEdgeAttr("a", "b", "weight", 1.0);   // no implicit weight — name it
g.addEdge("b", "c");
g.setEdgeAttr("b", "c", "weight", 2.0);

PathResult p = ShortestPaths.dijkstra(g, "a", "c", "weight");
float64[] pr = PageRank.compute(g);            // index-shaped, joins via nodeAt(i)
LouvainResult r = Louvain.run(g, (uint64) 42); // the seed is mandatory
```

Nodes are strings at the boundary, contiguous insertion-order indices
inside; every result is index-shaped and joins back through `nodeAt` /
`GraphData.nodeIds`. Edge lists cross from a `cajeta.nucleo.frame.Table`
via `Graph.fromTable` / `fromTableAttrs` (string id columns, `float64`
attribute columns).

## The surface

- **The graph type** — directed/undirected simple graphs (duplicate
  `addEdge` updates), self-loops, named `float64` edge attributes (unset
  is a loud throw, never a silent 1.0), and **typed edges** (one
  interned type name per edge — the `cajeta-rag` relation shape).
- **Traversal & connectivity** — BFS/DFS with visit order deterministic
  **by contract** (edge-insertion neighbour order); connected components,
  weak/strong (Kosaraju) — with the wrong verb for the graph's
  directedness refused loudly.
- **Shortest paths** — unweighted hops or a named weight attribute
  (negative weights refused); unreachable is an explicit `reachable()`
  answer, never an infinity; all-pairs into a `DistMatrix`.
- **Centrality** — degree (in/out), eigenvector (explicit
  `maxIter`/`tol`), closeness, betweenness — exact Brandes or seeded
  source-sampling that is **exact at k = n** — and **PageRank**
  (NetworkX defaults; rank sinks redistribute; `reversed()`,
  personalized, weighted forms).
- **Communities** — Louvain with a **mandatory seed** (same seed, same
  partition, any machine), resolution knob, the full dendrogram; and
  `Modularity` to score any partition from any source.
- **The drawing boundary** — `GraphData` emits identities, endpoint
  index arrays, weights, and type names for `dev.cajeta.chart`;
  `toCsr()` exports the adjacency for `cajeta.math.linalg`.

## Parity oracles

Oracles are a muse, never a port:

- **NetworkX 3.6.1** — construction, traversal, centrality.
- **python-louvain 0.16** — community detection (treated with the caution
  a single-purpose package deserves; divergence is a finding to
  investigate, not automatically a bug).

Fixture generators live in `tools/fixtures/` and assert the exact pins;
the oracle venv is `code/ml/venv-graph-ref` (numpy 2.5.1). Deliberate
departures are catalogued in
[Differences from NetworkX](docs/DifferencesFromNetworkX.md).

## Build, test, tour

```sh
cajeta build        # emits build/archive/dev.cajeta.graph-<version>.cja
./run-tests.sh      # builds the .cja + cajeta-unit test binary, runs it
./run-tour.sh       # the self-checking 14-section tour (also: cajeta tour)
```

`run-tests.sh` honors `CAJETA` (compiler path), `UNIT_REPO` / `UNIT_CJA`
(cajeta-unit resolution), falling back to the Olla registry at the pin in
`cajeta.json`. `scripts/bench.sh` runs the scaling benchmarks behind
[docs/scaling.md](docs/scaling.md).

Spec: `cajeta-six/specs/archive/ml-graph-analytics-spec.md`. Plan:
`cajeta-six/agents/archive/ml-graph-analytics-plan.md` (complete).
License: Apache-2.0.
