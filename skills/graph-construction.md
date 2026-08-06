---
id: graph-construction
applies-to: [dev.cajeta.graph.Graph]
title: Building graphs — factories, typed edges, named attributes, Table edge lists
description: Graph construction and its contracts — factory-only creation (directed/undirected), string identity with insertion-order indices, duplicate addEdge UPDATES, one interned type per edge, NaN-backed named float64 attributes that throw when read unset, and fromTable/fromTableAttrs column expectations (string id columns, float64 attrs, srcId/dstId naming).
---

# Building graphs

```cajeta
import dev.cajeta.graph.Graph;

Graph g = Graph.undirected();          // factory-only; ctor is private
g.addEdge("a", "b");                   // creates unknown nodes; returns edge id
g.setEdgeAttr("a", "b", "weight", 1.0);
g.addTypedEdge("a", "c", "imports");   // one interned type name per edge
int64 i = g.indexOf("a");              // insertion-order index; -1 if absent
```

- `Graph.directed()` keeps `(u,v)` and `(v,u)` distinct; undirected
  treats them as the same edge.
- **Duplicate `addEdge` UPDATES** — returns the existing edge id,
  changes nothing, attributes kept. Parallel edges cannot exist.
- Self-loops are legal; an undirected self-loop adds 2 to `degree`.
- `edgeType(u, v)` answers `""` for untyped (throws on a missing edge);
  `neighborsByType(id, type)` with an unknown type is an EMPTY LIST,
  not an error. `neighborsOf(id)` is edge-insertion order — stable.

## Attributes: named, loud when unset

No implicit weight anywhere. `edgeAttr(u, v, name)` throws when the
edge, the attribute column, or the cell is unset — probe with
`hasEdgeAttr` first when absence is expected. Internally: dense
per-name columns, NaN = unset.

## From a Table edge list

```cajeta
import cajeta.nucleo.frame.Table;
import cajeta.nucleo.column.Column;
import cajeta.nucleo.column.StringColumn;

public record EdgeRow { Utf8 srcId; Utf8 dstId; float64 w; }

Table<EdgeRow> t = heap Table<EdgeRow>(
    StringColumn.of(sv), StringColumn.of(dv), Column.of<float64>(wv));
String[] attrs = heap String[1];
attrs[0] = "w";
Graph g = Graph.fromTableAttrs(t, "srcId", "dstId", true, attrs);
```

- `srcCol`/`dstCol` MUST be string columns — nothing is stringified;
  integer ids must already be strings. Attribute columns MUST be
  `float64` and attach under their own names.
- One row = one `addEdge`: duplicate rows collapse; the LAST row's
  attribute values win. Node indices follow first appearance.
- Name record fields `srcId`/`dstId`, **not** `src`/`dst` — `Table`
  owns a `src` member and accessor synthesis refuses to shadow it.
- `fromTable(t, s, d, directed)` = the zero-attributes form.

Factories return `#Graph` (owned). `nodeAt(i)` returns a borrow.

Related: [[graph-overview]], [[graph-data-boundary]] (getting structure
back out), [[graph-traversal-paths]].
