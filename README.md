# cajeta-graph

Network analysis for the cajeta ecosystem: `dev.cajeta.graph`.

- Directed and undirected graphs with weights, attributes, and **typed
  edges**; construction from `cajeta.nucleo.frame.Table` edge lists.
- Traversal (deterministic BFS/DFS), connectivity, shortest paths.
- Centrality: degree, eigenvector, **PageRank**, betweenness (Brandes,
  exact and sampled), closeness.
- Louvain community detection and modularity.

Graph analytics is not machine learning — nothing here uses the estimator
protocol — so the library depends on the stdlib alone. It also draws
nothing: graph data is emitted for `dev.cajeta.chart` to render.

## Parity oracles

Oracles are a muse, never a port:

- **NetworkX 3.6.1** — construction, traversal, centrality.
- **python-louvain 0.16** — community detection (treated with the caution
  a single-purpose package deserves; divergence is a finding to
  investigate, not automatically a bug).

Fixture generators live in `tools/fixtures/` and record the exact pins;
the oracle venv is `code/ml/venv-graph-ref` (numpy 2.5.1).

## Build and test

```sh
cajeta build        # emits build/archive/dev.cajeta.graph-<version>.cja
./run-tests.sh      # builds the .cja + cajeta-unit test binary, runs it
```

`run-tests.sh` honors `CAJETA` (compiler path), `UNIT_REPO` / `UNIT_CJA`
(cajeta-unit resolution), falling back to the Olla registry at the pin in
`cajeta.json`.

Spec: `cajeta-six/specs/ml-graph-analytics-spec.md`. Plan:
`agents/ml-graph-analytics-plan.md`.
