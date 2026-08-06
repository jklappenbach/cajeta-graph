---
id: graph-centrality
applies-to: [dev.cajeta.graph.Centrality, dev.cajeta.graph.PageRank]
title: Centrality & PageRank — NetworkX conventions, explicit eigenvector params, seeded sampling, sinks that redistribute
description: The centrality family as index-shaped float64[] — degree (in/out variants throw on undirected), eigenvector with MANDATORY maxIter/tol and a no-last-iterate convergence throw, closeness (isolated = 0, directed uses incoming), exact vs seeded-sampled Brandes betweenness (k = n IS exact), and PageRank with NetworkX defaults, reversed/personalized/weighted forms, and sink redistribution.
---

# Centrality & PageRank

All results are index-shaped `#float64[]` — join via `g.nodeAt(i)`.
Conventions and pinned numbers are NetworkX 3.6.1's. Everything is
all-zeros below two nodes.

```cajeta
import dev.cajeta.graph.Centrality;
import dev.cajeta.graph.PageRank;

float64[] dc = Centrality.degree(g);
float64[] ev = Centrality.eigenvector(g, (int64) 100, 0.000001); // NO defaults
float64[] bw = Centrality.betweenness(g, true);                  // exact Brandes
float64[] bs = Centrality.betweennessSampled(g, k, (uint64) 42, true);
float64[] pr = PageRank.compute(g);          // 0.85 / 100 / 1e-6 built in
```

## The hazards, in order of bite

- **`eigenvector` / `eigenvectorWeighted` have NO default arguments** —
  pass `maxIter=100, tol=1e-6` to match NetworkX. Non-convergence
  THROWS and the last iterate is NOT returned (raise maxIter or loosen
  tol). PageRank behaves the same on non-convergence.
- **`inDegreeCentrality`/`outDegreeCentrality` throw on an undirected
  graph** — use `degree`. Directed `degree` counts in+out.
- **Sampled betweenness is the scaling escape hatch**: seeded Philox
  sources without replacement, scaled n/k, error O(1/√k). **`k >= n`
  short-circuits to exact — bit-identical.** Exact Brandes goes
  non-interactive around n ≈ 1000 (docs/scaling.md); sample above that.
- `betweennessEndpoints(g, normalized)` is NetworkX `endpoints=True` as
  a separate verb. Closeness: isolated nodes are 0; directed closeness
  uses INCOMING distances (NetworkX default).

## PageRank

`compute` / `reversed` / `personalized` / `weighted`, and
`full(g, damping, maxIter, tol, pers, weightAttr, reverse)` (empty
`pers` = uniform, `""` = unweighted).

- **Rank sinks redistribute, never absorb** — mass flows through the
  personalization vector, scores always sum to 1. A leaf that
  everything imports ranks HIGHEST, it does not soak.
- `reversed(g)` ranks by outbound influence without rebuilding the
  graph. `personalized`: unreachable nodes get exactly 0; the vector is
  normalized for you (zero-sum throws, wrong length throws).
- Weighted forms: negative weight throws; missing attribute throws
  ([[graph-construction]] — no implicit weight).

Related: [[graph-overview]], [[graph-traversal-paths]],
[[graph-data-boundary]] (joining scores back to identities).
