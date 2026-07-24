#!/usr/bin/env bash
# Thin wrapper: render this slide folder via the one shared implementation.
# See scripts/render-d2.sh for the real logic and toolchain notes.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../../../.." && pwd)"
exec "$repo_root/scripts/render-d2.sh" "$here" "$@"
