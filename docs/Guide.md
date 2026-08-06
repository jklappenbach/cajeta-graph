# cajeta-graph guide

Everything below is the shipped 0.1.0 surface; each behavior is pinned by
the test suite (`src/test/cajeta`, 42 tests) or demonstrated by the
self-checking [tour](Tour.md).

## The graph type

### Identity: strings at the boundary, indices inside

Nodes are `String` identities at the API. Internally each node gets a
contiguous index `0..nodeCount()-1` in insertion order, with a
bidirectional map:

- `addNode(id)` — idempotent; returns the index (existing one if present).
- `indexOf(id)` — **-1 when absent, never a throw**; `hasNode(id)`.
- `nodeAt(i)` — the identity for an index (borrow).

That index is the join key for the whole library: every algorithm result
is index-shaped (`float64[]` centrality, `int64[]` component or community
labels), and joins back through `nodeAt` / `GraphData.nodeIds`. Integer
node ids must enter as their string form — the `Table` path stringifies
nothing; use string columns.

### Simple graphs, directed or undirected

`Graph.undirected()` treats `(u,v)` and `(v,u)` as the same edge;
`Graph.directed()` keeps them distinct. The graph is **simple**: a
duplicate `addEdge(u, v)` updates the existing edge (returns its id,
alters nothing); parallel edges cannot exist; multigraphs are out of
scope. Self-loops are allowed and contribute 2 to an undirected degree
(the NetworkX rule). `addEdge` creates unknown endpoints as it goes.

Degrees: `degree`, `inDegree`/`outDegree` (directed), `degreeAt(i)` by
index. `density()` is `m/(n(n-1))` directed, doubled undirected, and 0
below two nodes. `neighborsOf(id)` returns neighbours in
**edge-insertion order** — deterministic, part of the contract.

### Typed edges

An edge carries at most one interned type name; untyped is `""`.

- `addTypedEdge(u, v, type)` — as `addEdge`, then sets/updates the type.
- `edgeType(u, v)` — the name, or `""`; throws on a missing edge.
- `neighborsByType(id, type)` — filtered neighbours; an unknown type is
  an **empty list**, not an error.

This is the `cajeta-rag` relation-graph shape (`imports` / `calls` /
`links-to` / `cites`): one graph, edges distinguished by type.

### Edge attributes — no implicit weight

There is no built-in weight. Edges carry named `float64` attributes
(`setEdgeAttr`, `edgeAttr`, `hasEdgeAttr`), and **every weighted
algorithm names the attribute it reads**. An unset attribute is loud: a
`GraphException` at use, never a silent 1.0. Internally attributes are
dense per-name columns with NaN = unset; `hasEdgeAttr` is how absence is
inspected without throwing.

### Construction from a Table edge list

NetworkX's `from_pandas_edgelist` shape over `cajeta.nucleo.frame.Table`:

```cajeta
public record EdgeRow { Utf8 srcId; Utf8 dstId; float64 w; }

Table<EdgeRow> t = heap Table<EdgeRow>(
    StringColumn.of(sv), StringColumn.of(dv), Column.of<float64>(wv));
String[] attrs = heap String[1];
attrs[0] = "w";
Graph g = Graph.fromTableAttrs(t, "srcId", "dstId", true, attrs);
```

- `srcCol`/`dstCol` must be **string columns**; attribute columns must be
  `float64` and attach under their own names.
- One row = one `addEdge`: duplicate rows collapse onto one edge and the
  last row's attribute values win; node indices follow first appearance.
- `fromTable(t, srcCol, dstCol, directed)` is the no-attributes form.
- Schema note: the record fields are `srcId`/`dstId`, not `src`/`dst` —
  `Table` itself owns a `src` member and the per-column accessor
  synthesis refuses to shadow it.

### The index-shaped surface

For algorithm authors, `Graph` exposes a flat, by-index view:
`edgeCountAt`/`edgeAt` (out-incidence), `inEdgeCountAt`/`inEdgeAt`,
`edgeSrc`/`edgeDst`/`edgeOther`, `edgeIdOf`, and the type table
(`edgeTypeIdOf`, `typeNameOf`, `typeIdOf`). Adjacency is a purpose-built
per-node insertion-ordered incident-edge list over a flat edge table —
deliberately **not** `CsrMatrix`, which is construction-immutable and
serves as the export format instead (see the drawing boundary, below).

## Traversal

`Traversal.bfs(g, source)` and `Traversal.dfs(g, source)` return the
visit order as `ArrayList<String>`. Order is **deterministic by
contract**: FIFO (BFS) or preorder (DFS) over edge-insertion neighbour
order — repeated runs produce identical sequences, and the test suite
pins exact orders. Unreachable nodes are omitted. Unknown sources throw.

## Connectivity

Index-shaped `int64[]` labels, component ids in discovery order from
node 0 (stable enough to pin as fixtures):

- `Components.connected(g)` — undirected only; **throws on a directed
  graph** with directions to the right verb.
- `Components.weaklyConnected(g)` — directed, edges read both ways.
- `Components.stronglyConnected(g)` — Kosaraju; undirected graphs throw.
- `Components.componentCount(labels)`.

Component structure is pinned against NetworkX 3.6.1.

## Shortest paths

- `ShortestPaths.bfsPath(g, src, dst)` — unweighted hops.
- `ShortestPaths.dijkstra(g, src, dst, weightAttr)` — sums the named
  attribute; **negative weights are refused** (Dijkstra's invariant),
  missing attributes throw.

Both return a `PathResult`: `reachable()`, `distance()`, `path()`
(source..target, borrow). **Unreachable is an explicit answer** —
`distance()`/`path()` on an unreachable result throw; there is no
infinity in the API.

- `ShortestPaths.allPairs(g)` — BFS from every node, Θ(n·(n+m)).
- `ShortestPaths.allPairsWeighted(g, weightAttr)` — Dijkstra from every
  node; the dense-scan implementation makes this Θ(n³) — a small-graph
  tool (n ≲ 500).

Both return a `DistMatrix`: `size()`, `reachableAt(i, j)`,
`distAt(i, j)` (throws on an unreachable pair). Indexing is node-index
order. Measured numbers and the n = 2000 ceiling: [scaling](scaling.md).

## Centrality

All functions return index-shaped `#float64[]`, NetworkX 3.6.1
conventions, all-zeros below two nodes.

- `Centrality.degree(g)` — `degree/(n−1)`; directed counts in+out.
  Directed-only refinements: `inDegreeCentrality`, `outDegreeCentrality`
  (undirected graphs throw, pointing back at `degree`).
- `Centrality.eigenvector(g, maxIter, tol)` /
  `eigenvectorWeighted(g, maxIter, tol, attr)` — NetworkX's exact power
  iteration (`x' = x + Aᵀx`, L2-normalized, converged at
  `Σ|x'−x| < n·tol`). **No default arguments** — callers state
  `maxIter`/`tol` (NetworkX's defaults are 100 and 1e-6).
  Non-convergence **throws; the last iterate is not returned**.
- `Centrality.closeness(g)` — NetworkX convention with the
  reachable-fraction factor; isolated nodes are 0; directed graphs use
  incoming distances (the NetworkX default).
- `Centrality.betweenness(g, normalized)` — exact Brandes over
  unweighted BFS. `betweennessEndpoints(g, normalized)` is the
  `endpoints=True` variant.
- `Centrality.betweennessSampled(g, k, seed, normalized)` — Brandes from
  `k` seeded sample sources (Philox, without replacement), scaled `n/k`.
  An approximation with standard error O(1/√k) — **`k = n` is exact**,
  identical output. This is the scaling escape hatch: measured crossover
  and recommendations in [scaling](scaling.md).

## PageRank

`PageRank.compute(g)` uses damping 0.85, maxIter 100, tol 1e-6, uniform
personalization, unweighted — NetworkX's defaults. Variants:
`reversed(g)` (outbound influence, no graph rebuild), `personalized(g,
pers)` (`pers` is scaled to sum 1), `weighted(g, attr)`, and the full
form `full(g, damping, maxIter, tol, pers, weightAttr, reverse)` where
empty `pers` means uniform and `""` means unweighted.

**Rank sinks redistribute, never absorb**: a node with no out-edges
spreads its mass through the personalization vector each step, so scores
always sum to 1 — the dependency-graph case (a leaf utility imported by
everything) ranks highest instead of soaking rank into a dead end.
Throws: personalization length mismatch or zero sum, negative weights,
missing weight attribute, and non-convergence (the last iterate is not
returned).

## Communities — Louvain and modularity

`Modularity` scores **any** partition, from any source:
`of(g, labels)` (γ = 1, unweighted), `weighted(g, labels, attr)`,
`at(g, labels, resolution, attr)`. Undirected notion only — directed
graphs throw. γ scales the null-model term; γ = 1 is standard
modularity. Self-loops count once in the community's internal weight,
twice in its degree sum (the NetworkX rule).

`Louvain.run(g, seed)` / `Louvain.full(g, seed, resolution, weightAttr,
init)` — **the seed is mandatory; an unseeded run does not exist in this
API.** Node visit order is a seeded Philox permutation, so the same seed
reproduces the partition exactly, on any machine. Higher resolution →
more, smaller communities; note **python-louvain's parameter is the
inverted convention** (a recorded finding, deliberately not "fixed").
Directed graphs and negative weights throw; an `init` partition seeds
level 0; empty `init` means singletons.

`LouvainResult` exposes the full dendrogram, not just the answer:
`labels()` (final, node-shaped), `communityCount()`, `sizeOf(c)`,
`modularity()` (Q at the run's γ and weights), `levelCount()`,
`labelsAtLevel(l)` (each level original-node shaped; the last level IS
the final partition; community count never increases going up).
`Louvain.countOf(labels)` counts distinct labels in any label array.

Partitions are pinned against python-louvain 0.16 on shared fixtures and
modularity values against NetworkX 3.6.1.

## The drawing boundary

Nothing in this library draws, and there is deliberately no layout API.
Structure crosses to `dev.cajeta.chart` as plain data via `GraphData`:

- `nodeIds(g)` — identities in index order (the join key).
- `edgeSources(g)` / `edgeTargets(g)` — endpoint node indices, edge-id
  ordered.
- `edgeWeights(g, attr)` — per-edge values of a named attribute (unset
  throws).
- `edgeTypes(g)` — per-edge type names, `""` for untyped.

For linear algebra, `Graph.toCsr()` exports the adjacency as a
`cajeta.nucleo.sparse.CsrMatrix` (entry 1.0 per edge; an undirected edge
contributes both orientations, so nnz = 2m − selfLoops), and
`toCsrWeighted(attr)` uses the named attribute — the on-ramp to spectral
methods through `cajeta.math.linalg`.

## Error policy and determinism

One error type: `GraphException` (a `RecoverableException`) for contract
violations a caller can handle — unknown node, missing edge or
attribute, a negative weight handed to Dijkstra, a directed graph handed
an undirected-only verb. **Everything is a throw; nothing warns or
prints** — there are zero print sites in the library. Two lookups answer
in-band instead of throwing: `indexOf` (-1) and `neighborsByType` on an
unknown type (empty list).

Determinism: neighbour order is edge-insertion order (contractual);
traversal orders are pinned; every source of randomness — Louvain visit
order, betweenness sampling — takes an explicit `uint64` seed (Philox),
so the same inputs and seeds are bit-identical on every machine.

## What is not here (0.1.0)

Stated so you don't hunt for it:

- **Structural measures beyond density** — no clustering coefficient, no
  diameter/average path length aggregate, no degree-distribution helper
  (spec §6; `DistMatrix` has the raw distances if you need an aggregate).
- **Multigraphs** — out of scope; duplicate edges update.
- **Eigenvector-centrality default arguments** — pass `maxIter`/`tol`
  yourself (PageRank has defaulted forms; eigenvector does not).
- **A Table join-back helper** — results join by index through
  `nodeAt`/`nodeIds` by convention; no helper builds the joined `Table`.
- **Layout / drawing** — by design, never coming here; that is
  `dev.cajeta.chart`'s side of the boundary.

The full divergence catalogue:
[Differences from NetworkX](DifferencesFromNetworkX.md).
