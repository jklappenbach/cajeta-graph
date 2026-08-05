# Scaling — measured (plan 5.1.1–5.1.2, spec §8.3)

Measured, not asserted. Reproduce with:

```sh
CAJETA=<toolchain>/build/src/cajeta ./scripts/bench.sh
```

Machine of record: 32-core Linux workstation, toolchain 0.16.0-pre,
2026-08-05. Graphs: seeded (Philox) sparse random, average degree ≈ 8.
Times are machine-dependent; the SHAPE (growth factors, crossover) is
what the recommendations rest on.

## Exact vs sampled betweenness — the §8.3 crossover

| n | edges | exact (ms) | sampled k=64 (ms) | max abs err (normalized) |
|------:|------:|-----------:|------------------:|-------------------------:|
| 250 | 974 | 67 | 17 | 0.0104 |
| 500 | 1 986 | 276 | 35 | 0.0114 |
| 1 000 | 3 983 | 1 106 | 73 | 0.0132 |
| 2 000 | 7 978 | 4 445 | 146 | 0.0148 |
| 4 000 | 15 978 | 17 977 | 297 | 0.0065 |

Exact Brandes is Θ(n·m) — ×4 per doubling on these graphs; sampling at
fixed `k` is Θ(k·m) — linear in n. **The measured crossover: exact stops
being interactive (>1 s) at n ≈ 1 000 and reaches ~18 s by n = 4 000,
while k=64 sampling holds under 0.3 s with max absolute error ≤ 0.015 on
normalized values.**

Recommendation (documented on `Centrality.betweennessSampled`): exact by
default up to a few thousand nodes; above that, sample. The estimator's
standard error shrinks as O(1/√k); `k = n` reproduces exact output
identically (pinned in `CentralityTest`).

## All-pairs shortest paths — the size ceiling

Unweighted all-pairs (`ShortestPaths.allPairs`, Θ(n·(n+m)) BFS per
source, n² result matrix):

| n | edges | time | result memory |
|------:|------:|-----:|--------------:|
| 2 000 | 7 988 | 2.2 s | 32 MB (n² × f64) |

**Documented ceiling: n = 2 000 completes in ~2 s** — the budget stated
by plan 5.1.2 is 60 s, met with ×25 headroom, but the n² result matrix
is the real wall: n = 10 000 would need 800 MB before any time is spent.
The weighted form (`allPairsWeighted`) is Θ(n³) with the dense-scan
Dijkstra and should be treated as a small-graph tool (n ≲ 500).

## The drawing boundary (spec §8.1)

Nothing here draws and no layout is computed — `GraphData` emits
identity lists, endpoint index arrays, weights, and types;
`Graph.toCsr` emits the sparse adjacency. Positions belong to
`dev.cajeta.chart`.
