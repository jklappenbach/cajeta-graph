# The cajeta-graph tour, narrated

Run it with `cajeta tour` (or `./run-tour.sh`). The tour is self-checking:
every claim below is asserted at runtime, and the process exits non-zero
if any stops being true. Source: `tour/src/dev/cajeta/graph/tour/Tour.cajeta`.

Every graph is built explicitly and every seeded algorithm gets an
explicit seed — no files, no ambient RNG — so the tour behaves
identically on every machine. The recurring fixtures: the weighted **a–g
graph** with an isolated `h`, the **star** (hand-checkable centrality),
the **dependency graph** whose leaf `util` is a rank sink, the
**barbell** (two 5-cliques on a bridge), and a **chain of three
triangles** (resolution behavior).

1. **Construction.** Nodes are strings at the boundary; each gets a
   contiguous insertion-order index inside — the join key for every
   array-shaped result. `indexOf` answers -1 for an unknown id, `addNode`
   is idempotent, and density is defined (0 below two nodes).
2. **Directed vs undirected, typed edges.** The same edge set means
   different things: `app→lib1` exists while `lib1→app` does not; in- and
   out-degree split. Edges optionally carry one interned type name —
   `neighborsByType` filters by it, untyped edges answer `""`, and an
   unknown type is an empty list, not an error.
3. **Edge attributes.** No implicit weight: attributes are named, unset
   is visible via `hasEdgeAttr`, and a duplicate `addEdge` updates the
   existing edge — count unchanged, attributes kept.
4. **Table construction.** NetworkX's `from_pandas_edgelist` shape: name
   the string source/target columns of a `Table<EdgeRow>`, and remaining
   `float64` columns attach by name as edge attributes. Four rows become
   four edges; the `w` column rides along.
5. **Traversal.** BFS order `a b d c e f g` and DFS preorder
   `a b c f e d g` — deterministic by contract (edge-insertion neighbour
   order), asserted identical on a second run.
6. **Components.** Undirected: a–g is one component, `h` its own.
   Directed graphs get separate verbs — weakly connected merges across
   edge direction; strongly connected (Kosaraju) keeps the `x→y→z→x`
   cycle together and splits the rest. Asking the wrong verb throws.
7. **Shortest paths.** `bfsPath` counts hops (a→g in 3); `dijkstra` sums
   the named weight attribute (a→g is 4.0 along `a b c g`).
   Unreachability is an explicit answer — `reachable()` false, and
   `distance()` would throw rather than mint an infinity.
8. **All-pairs.** `DistMatrix` from BFS (or Dijkstra) at every node,
   indexed by node index; unreachable pairs answer `reachableAt` false.
9. **Centrality.** The star makes each measure hand-checkable: degree
   centrality (center 1.0, leaves 0.25), eigenvector (center ≈ 0.7071 —
   no default arguments, `maxIter`/`tol` are yours), betweenness (raw
   6.0, normalized exactly 1.0), and closeness (an isolated node is 0).
10. **Sampled betweenness.** Exact Brandes is Θ(n·m); seeded
    source-sampling is Θ(k·m) with error O(1/√k). `k = n` reproduces the
    exact numbers bit for bit; `k = n/2` stays within the stated band.
    The measured crossover lives in [scaling](scaling.md).
11. **PageRank.** On the dependency graph the leaf `util` ranks highest
    (0.4210…, matching NetworkX to six figures) and scores sum to 1 —
    rank sinks redistribute rather than absorb. `reversed()` ranks by
    outbound influence without rebuilding; personalized PageRank gives an
    unreachable node exactly 0.
12. **Communities.** Louvain's seed is mandatory: the same seed
    reproduces the barbell partition exactly — two communities of five,
    Q = 0.4523809524. `Modularity.of` scores the same labels
    identically; it will score any partition from any source.
13. **Resolution and the dendrogram.** γ = 0.05 merges the triangle
    chain into one community, γ = 1 finds the three triangles, γ = 4
    splits further. Every level is exposed, original-node shaped; the
    last level is the final partition.
14. **The drawing boundary.** Nothing here draws. `GraphData` emits
    identities, endpoint index arrays, per-edge weights and type names;
    index-shaped results join back through the identity list. `toCsr()`
    exports the adjacency for `cajeta.math.linalg` — nnz = m directed,
    2m undirected.
