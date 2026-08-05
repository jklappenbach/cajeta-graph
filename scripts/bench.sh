#!/usr/bin/env bash
# Build + run the scaling benchmarks (plan 5.1.1–5.1.2) behind
# docs/scaling.md. Override the compiler with CAJETA=<path>.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
CAJETA="${CAJETA:-cajeta}"

out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT

echo ">> building graph library .cja"
"$CAJETA" --emit=cja -o "$out/graph.cja" \
    dev.cajeta.graph.GraphLib.run "$here/src/main/cajeta" "$out" >/dev/null

echo ">> building + running the bench binary"
"$CAJETA" --emit=exe \
    --classpath="$out/graph.cja" \
    -o "$out/graphbench" \
    dev.cajeta.graph.bench.BenchMain.run "$here/bench/cajeta" "$out" >/dev/null

"$out/graphbench"
