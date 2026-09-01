#!/bin/bash
# build.sh - Build the CallHub MCPB extension bundle.
#
# Vendors runtime dependencies into src/lib/ (so the bundle needs no runtime
# pip install) and packs everything into callhub.mcpb.
#
# Requirements: python3 (>=3.10), and the mcpb CLI (npx @anthropic-ai/mcpb).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "==> Cleaning previous build output"
rm -rf src/lib
rm -f callhub.mcpb

echo "==> Vendoring dependencies into src/lib"
python3 -m pip install \
  --target src/lib \
  --no-compile \
  --upgrade \
  -r requirements.txt

echo "==> Validating manifest"
npx --yes @anthropic-ai/mcpb@2 validate manifest.json

echo "==> Packing bundle"
npx --yes @anthropic-ai/mcpb@2 pack . callhub.mcpb

echo "==> Done: $(ls -lh callhub.mcpb | awk '{print $5}') -> callhub.mcpb"
