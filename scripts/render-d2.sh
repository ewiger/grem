#!/usr/bin/env bash
# Shared D2 renderer for grem "visual story" slide folders.
#
# There is exactly one real rendering implementation (this script); each slide
# folder ships a thin build.sh that delegates here. It compiles every NN-*.d2 in
# a folder to a committed .svg so the diagrams render in plain Markdown viewers
# (GitHub, IDE preview) without anyone installing the D2 toolchain. It can also
# rasterize each .svg to .png via librsvg when WITH_PNG=1.
#
# Usage:
#   scripts/render-d2.sh <slide-folder>       # SVG only (default)
#   WITH_PNG=1 scripts/render-d2.sh <folder>  # also emit PNG via rsvg-convert
#
# Toolchain (Homebrew):  brew install d2 librsvg
# Docker fallback (no local d2):
#   docker run --rm -v "$PWD":/w -w /w terrastruct/d2:latest in.d2 out.svg
set -euo pipefail

dir="${1:?usage: render-d2.sh <slide-folder>}"

# Homebrew installs to /opt/homebrew/bin (Apple Silicon) or /usr/local/bin,
# neither of which is guaranteed on a non-login shell PATH.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if ! command -v d2 >/dev/null 2>&1; then
  {
    echo "error: d2 not found. Install with 'brew install d2', or render one file"
    echo "       with the Docker fallback:"
    echo "         docker run --rm -v \"\$PWD\":/w -w /w \\"
    echo "           terrastruct/d2:latest in.d2 out.svg"
  } >&2
  exit 1
fi

shopt -s nullglob
count=0
for src in "$dir"/[0-9][0-9]-*.d2; do
  svg="${src%.d2}.svg"
  echo "d2  $src -> $svg"
  d2 "$src" "$svg"
  if [[ "${WITH_PNG:-0}" == "1" ]]; then
    if command -v rsvg-convert >/dev/null 2>&1; then
      png="${src%.d2}.png"
      echo "png $svg -> $png"
      rsvg-convert "$svg" -o "$png"
    else
      echo "warn: WITH_PNG=1 but rsvg-convert not found; skipping PNG" >&2
    fi
  fi
  count=$((count + 1))
done

if [[ "$count" -eq 0 ]]; then
  echo "warn: no NN-*.d2 files in $dir" >&2
fi
echo "rendered $count diagram(s) from $dir"
