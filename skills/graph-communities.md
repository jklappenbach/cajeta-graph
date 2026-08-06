---
id: graph-communities
applies-to: [dev.cajeta.graph.Louvain, dev.cajeta.graph.LouvainResult, dev.cajeta.graph.Modularity]
title: Louvain & modularity — mandatory seed, resolution direction, the dendrogram, scoring any partition
description: Community detection with a MANDATORY uint64 seed (same seed = identical partition), γ that scales the null model (higher = smaller communities; python-louvain's parameter is INVERTED), the exposed dendrogram via labelsAtLevel, undirected-only (directed throws), and Modularity as a standalone scorer for partitions from any source.
---

# Louvain & modularity

Undirected notion only — **a directed graph throws** from both
`Modularity` and `Louvain`; build the undirected graph instead.

```cajeta
import dev.cajeta.graph.Louvain;
import dev.cajeta.graph.LouvainResult;
import dev.cajeta.graph.Modularity;

LouvainResult r = Louvain.run(g, (uint64) 42);     // seed is MANDATORY
int64[] labels = r.labels();                        // node-index shaped, owned
float64 q = r.modularity();                         // Q at the run's γ/weights
float64 q2 = Modularity.of(g, labels);              // score ANY partition
```

- **The seed is mandatory — an unseeded run does not exist.** Visit
  order is a seeded Philox permutation: same seed, same partition,
  bit-identical, any machine. (python-louvain's `random_state` is
  optional; here reproducibility is not.)
- Full form: `Louvain.full(g, seed, resolution, weightAttr, init)` —
  `""` = unweighted, empty `init` = singleton start, otherwise `init`
  seeds level 0 (length must equal node count).
- **Resolution direction**: γ scales the null-model term; γ = 1 is
  standard modularity; HIGHER γ → more, smaller communities (the
  NetworkX/Leiden convention). **python-louvain's parameter is
  inverted** — do not port thresholds across.
- Negative weights throw. n = 0 → empty result; total weight 0 →
  singletons with Q = 0.

## The dendrogram

`levelCount()` ≥ 1; `labelsAtLevel(l)` (0-based, owned copy,
original-node shaped) coarsens upward; **the last level IS the final
partition** (`Louvain.countOf(labelsAtLevel(levelCount()-1)) ==
communityCount()`). `sizeOf(c)` throws on an unknown community id.

## Modularity standalone

`of(g, labels)` (γ=1, unweighted), `weighted(g, labels, attr)`,
`at(g, labels, resolution, attr)`. Score partitions from ANY source —
comparing an external clustering against Louvain's is the intended use.
Labels must be dense `0..n-1`-ranged, length = node count (else throw).
Self-loops: once in internal weight, twice in degree sum (NetworkX
rule).

Related: [[graph-overview]], [[graph-construction]] (weights),
[[graph-data-boundary]] (labels join to identities by index).
