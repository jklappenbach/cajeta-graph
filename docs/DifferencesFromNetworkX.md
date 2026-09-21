# Differences from NetworkX

Recognizable, not faithful. NetworkX 3.6.1 is the behavioural muse —
numbers are pinned against it in the test suite — but where a NetworkX
convention encodes a genuine hazard, or just Python, this library
corrects it. python-louvain 0.16 is the community-detection oracle, held
to the caution a single-purpose package deserves: divergence there is a
finding to investigate, not automatically a bug.

- **No implicit weight.** NetworkX algorithms default to
  `weight="weight"` and silently treat a missing attribute as 1.0. Here
  every weighted algorithm **names its attribute**, and an unset value
  throws at use. A weighted computation over accidentally-unweighted
  edges is the classic silent-garbage path; it cannot happen here.

- **Everything is a throw; nothing warns.** NetworkX mixes exceptions
  (`NetworkXError`, `PowerIterationFailedConvergence`) with silent
  fallbacks. This library has exactly one error type
  (`GraphException`, recoverable) and **zero print sites** — including
  non-convergence of eigenvector centrality and PageRank, which throw
  and explicitly do **not** return the last iterate. Two lookups answer
  in-band instead: `indexOf` gives -1 and `neighborsByType` on an
  unknown type gives an empty list.

- **Unreachable is an explicit answer, not an exception or an
  infinity.** NetworkX raises `NetworkXNoPath` from shortest-path
  queries and omits pairs from distance dicts. Here `PathResult` and
  `DistMatrix` carry reachability (`reachable()`, `reachableAt`) you
  must check; asking for the distance of an unreachable pair throws.
  There is no `inf` anywhere in the API.

- **Simple graphs only; duplicate `addEdge` updates.** Same as
  `nx.Graph`/`nx.DiGraph` — but there is no `MultiGraph` at all, and no
  plan for one (spec §1.4). At most one type name per edge.

- **Deterministic order is a contract, not an accident.** NetworkX's
  visit orders fall out of dict insertion order and are not promised.
  Here neighbour order IS edge-insertion order by documented contract,
  the BFS/DFS sequences are pinned in the tests, and repeated runs are
  asserted identical.

- **Louvain's seed is mandatory.** python-louvain's `random_state` is
  optional, and an unseeded run is irreproducible. Here `Louvain.run` /
  `Louvain.full` require a `uint64` seed — an unseeded run does not
  exist in the API. Same seed, same partition, any machine.

- **Resolution follows the spec convention; python-louvain's is
  inverted.** Here γ scales the null-model term (γ = 1 is standard
  modularity; higher γ → more, smaller communities — the NetworkX /
  Leiden convention). python-louvain's `resolution` parameter has the
  opposite sense. Recorded as a finding; deliberately not asserted
  against.

- **Directed modularity is refused, not approximated.** NetworkX scores
  directed modularity with a directed null model. Here `Modularity` and
  `Louvain` implement the undirected notion only and **throw** on a
  directed graph, telling you to build the undirected one — quietly
  scoring a different objective would be worse.

- **The wrong connectivity verb throws.** `connected` on a directed
  graph, or `stronglyConnected` on an undirected one, is an error that
  names the right verb — mirroring NetworkX's
  `NetworkXNotImplemented`, but as the library's one exception type
  with a directive message.

- **Eigenvector centrality has no default arguments.** NetworkX
  defaults `max_iter=100, tol=1e-6`; here you pass both explicitly
  (those are the values to reach for). PageRank *does* carry the
  NetworkX defaults (0.85 / 100 / 1e-6) in its convenience forms.

- **Dijkstra is a dense scan, not a priority queue.** O(n²) per source,
  Θ(n³) for `allPairsWeighted` — deliberate simplicity for the 0.1
  small-graph scope; treat weighted all-pairs as a small-graph tool
  (n ≲ 500). Unweighted all-pairs is BFS-based, Θ(n·(n+m)), measured to
  n = 2000 in ~2 s ([scaling](scaling.md)).

- **Sampled betweenness is seeded and exact at k = n.** NetworkX's
  `k=` sampling uses its global RNG; here the sample is a seeded Philox
  draw without replacement, `k = n` short-circuits to the exact
  algorithm, and the tests pin that the two are bit-identical.

## Honestly not implemented

- **Clustering coefficient, diameter, average path length, degree
  distribution** — the spec's §6 structural measures, minus density,
  have not shipped in the 0.1 line.
- **Multigraphs** (`nx.MultiGraph`/`MultiDiGraph`) — out of scope.
- **Weighted traversal/centrality beyond the shipped forms** — no
  weighted betweenness or weighted closeness; eigenvector and PageRank
  are the weighted centralities.
- **A join-back helper** — index-shaped results join to identities
  through `nodeAt`/`GraphData.nodeIds` by convention; nothing builds
  the joined `Table` for you.
- **Layout and drawing** (`nx.spring_layout`, `nx.draw`) — by design,
  and never coming here: positions and rendering belong to
  `dev.cajeta.chart`, which consumes the `GraphData` payload.
