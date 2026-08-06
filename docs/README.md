# cajeta-graph documentation

Network analysis for cajeta: `dev.cajeta.graph`. Graphs with string
identities and typed edges, deterministic traversal, connectivity,
shortest paths, the centrality family with PageRank, and Louvain
community detection with modularity — all over the stdlib alone. Nothing
here uses the estimator protocol, and nothing here draws: structure is
emitted as plain data for `dev.cajeta.chart`.

| Page | What it covers |
|---|---|
| [Guide](Guide.md) | The graph type, every algorithm, API shapes, error policy |
| [Tour](Tour.md) | The runnable walkthrough (`cajeta tour`), section by section |
| [Differences from NetworkX](DifferencesFromNetworkX.md) | Where and why this library deliberately diverges — plus what is honestly not implemented |
| [Scaling](scaling.md) | Measured betweenness and all-pairs numbers, and the recommendations they support |

Agent-facing **skills** ship inside the `.cja` (`skills/*.md`, indexed):
`cajeta search-skill dev.cajeta.graph` / `list-skills` / `get-skills` (or
the same over cajeta-mcp) route a coding agent to the right verb, the
identity/join model, and the hazards — start at `graph-overview`.

Quick start:

```cajeta
Graph g = Graph.undirected();
g.addEdge("a", "b");
g.setEdgeAttr("a", "b", "weight", 1.0);
g.addEdge("b", "c");
g.setEdgeAttr("b", "c", "weight", 2.0);

PathResult p = ShortestPaths.dijkstra(g, "a", "c", "weight");
float64[] pr = PageRank.compute(g);           // index-shaped, joins via nodeAt(i)
LouvainResult r = Louvain.run(g, (uint64) 42); // the seed is mandatory
```

Parity oracles (a muse, never a port): **NetworkX 3.6.1** for
construction, traversal, and centrality; **python-louvain 0.16** for
community detection. Fixture generators in `tools/fixtures/` assert the
pins; the oracle venv is `code/ml/venv-graph-ref` (numpy 2.5.1).
