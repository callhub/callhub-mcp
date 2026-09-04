#!/bin/bash
# build-all.sh - Build per-platform CallHub MCPB bundles into dist/.
#
# Each platform bundle vendors the compiled dependencies for EVERY supported
# Python minor version (3.10-3.13) side by side. pydantic_core / rpds_py ship
# version-specific wheels (cp310/cp311/...), and their compiled .so/.pyd files
# carry the version tag in the filename, so multiple versions coexist in one
# lib/ directory and Python loads the one matching the running interpreter.
# Result: one bundle per platform that runs on any Python 3.10-3.13.
#
# Cross-platform wheels are downloaded on the build host (no execution needed).
# Requires: python3, and the mcpb CLI via npx @anthropic-ai/mcpb.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

PY_VERSIONS=(3.10 3.11 3.12 3.13 3.14)

# name:pip-platform-tag  (name is used for the output filename)
PLATFORMS=(
  "macos-arm64:macosx_11_0_arm64"
  "macos-x64:macosx_10_12_x86_64"
  "win-x64:win_amd64"
  "linux-x64:manylinux2014_x86_64"
)

mkdir -p dist
rm -f dist/*.mcpb

echo "==> Validating manifest"
npx --yes @anthropic-ai/mcpb@2 validate manifest.json

for entry in "${PLATFORMS[@]}"; do
  name="${entry%%:*}"
  tag="${entry##*:}"
  echo ""
  echo "==> Building $name ($tag)"

  rm -rf src/lib
  mkdir -p src/lib

  for py in "${PY_VERSIONS[@]}"; do
    echo "    - vendoring deps for Python $py"
    tmp="$(mktemp -d)"
    # Download binary-only wheels for this platform + python, then unpack each
    # into src/lib. Pure-python packages overwrite harmlessly; compiled modules
    # are version-tagged and coexist.
    python3 -m pip download \
      --only-binary=:all: \
      --platform "$tag" \
      --python-version "$py" \
      --implementation cp \
      -r requirements.txt \
      -d "$tmp" >/dev/null
    for whl in "$tmp"/*.whl; do
      python3 -m zipfile -e "$whl" src/lib >/dev/null
    done
    rm -rf "$tmp"
  done

  # Keep .dist-info — mcp calls importlib.metadata.version("mcp") at import time.

  out="dist/callhub-${name}.mcpb"
  npx --yes @anthropic-ai/mcpb@2 pack . "$out" >/dev/null
  echo "    -> $out ($(ls -lh "$out" | awk '{print $5}'))"
done

# Leave a clean native bundle in src/lib for local dev/testing.
rm -rf src/lib
echo ""
echo "==> All bundles built into dist/:"
ls -lh dist/*.mcpb
