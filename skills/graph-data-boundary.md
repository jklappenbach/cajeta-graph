---
id: graph-data-boundary
applies-to: [dev.cajeta.graph.GraphData]
title: The drawing boundary — GraphData payloads for chart, CSR export for LinAlg, index join-back
description: How structure leaves this library — GraphData's five arrays (nodeIds as THE join key, edge endpoint indices, named weights, type names), Graph.toCsr/toCsrWeighted for cajeta.math.linalg (undirected = both orientations), and the deliberate absences — no layout, no drawing, no Table join-back helper.
---

# The drawing boundary

Nothing in `dev.cajeta.graph` draws or computes positions — that is
`dev.cajeta.chart`'s side. Structure crosses as plain data:

```cajeta
import dev.cajeta.graph.GraphData;
import cajeta.collection.ArrayList;
import cajeta.nucleo.sparse.CsrMatrix;

ArrayList<String> ids = GraphData.nodeIds(g);     // index order — THE join key
int64[] src = GraphData.edgeSources(g);           // edge-id ordered
int64[] dst = GraphData.edgeTargets(g);
float64[] w = GraphData.edgeWeights(g, "weight"); // named; unset THROWS
ArrayList<String> ty = GraphData.edgeTypes(g);    // "" = untyped

CsrMatrix a = g.toCsr();                          // adjacency for LinAlg
```

## Join-back is by index, by convention

Every algorithm result (centrality `float64[]`, component/community
`int64[]`) is node-index shaped. `ids.get(i)` names the node behind
`scores[i]` — that positional agreement is the whole contract. There is
NO helper that builds a joined `Table`; do the loop yourself.

## CSR export

- `toCsr()`: entry 1.0 per edge. An undirected edge contributes BOTH
  orientations — nnz = m directed, 2m − selfLoops undirected. Node
  ordering is insertion order, same as everything else.
- `toCsrWeighted(attr)`: entries are the named attribute; **throws if
  the attribute is unset on any edge** — probe coverage first if edges
  may be partially attributed ([[graph-construction]]).
- Built via `CsrMatrix.fromCoo` — duplicate triplets would sum
  (scipy's rule), though a simple graph never produces them.

## Deliberately absent

No layout API, no rendering, no positions — pinned by test as a
non-feature. If you are looking for `spring_layout`, you want
`dev.cajeta.chart` consuming this payload.

Related: [[graph-overview]], [[graph-centrality]] (the scores you'll
join), [[graph-communities]] (the labels you'll join).
