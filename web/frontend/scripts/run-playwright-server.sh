#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STANDALONE_DIR="$ROOT_DIR/.next/standalone"
STANDALONE_STATIC_DIR="$STANDALONE_DIR/.next/static"

rm -rf "$STANDALONE_STATIC_DIR"
mkdir -p "$(dirname "$STANDALONE_STATIC_DIR")"
cp -R "$ROOT_DIR/.next/static" "$STANDALONE_STATIC_DIR"

if [[ -d "$ROOT_DIR/public" ]]; then
  rm -rf "$STANDALONE_DIR/public"
  cp -R "$ROOT_DIR/public" "$STANDALONE_DIR/public"
fi

cd "$ROOT_DIR"
exec node .next/standalone/server.js
