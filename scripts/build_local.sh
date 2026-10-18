#!/bin/bash
# Build the full bacp.dev and spec.bacp.dev site locally, the same way CI deploys it:
#   1. every release/YYYY-MM-DD branch -> /YYYY-MM-DD/ (mike), newest also aliased /latest/
#   2. main -> /draft/ (mike); with --draft-only, /draft/ is also aliased /latest/
#   3. the root landing site -> /
# Output: local_preview/   Serve with: python3 -m http.server 8000 -d local_preview
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=local_preview
DRAFT_ONLY=false
[[ "${1:-}" == "--draft-only" ]] && DRAFT_ONLY=true

uv sync -q
export PATH="$PWD/.venv/bin:$PATH"
export SPEC_URL="/latest/specification/overview/"
rm -rf "$OUT"

EXTRACT="draft latest versions.json"
if [[ "$DRAFT_ONLY" == false ]]; then
  git fetch origin 2>/dev/null || true
  git branch -f gh-pages origin/gh-pages 2>/dev/null || true
  for branch in $(git branch -a | grep -oE 'release/[0-9]{4}-[0-9]{2}-[0-9]{2}' | sort -u); do
    version=${branch#release/}
    EXTRACT="$EXTRACT $version"
    rm -rf build_temp && git worktree prune
    ref="$branch"; git show-ref --verify --quiet "refs/heads/$branch" || ref="origin/$branch"
    git worktree add -f build_temp "$ref"
    (cd build_temp && DOCS_MODE=spec BACP_BUILD_VERSION="$version" mike deploy "$version")
    git worktree remove -f build_temp
  done
fi

DOCS_MODE=spec BACP_BUILD_VERSION=draft mike deploy draft
[[ "$DRAFT_ONLY" == true ]] && mike alias -u draft latest

DOCS_MODE=root mkdocs build --strict -d "$OUT"
# shellcheck disable=SC2086
git archive gh-pages $EXTRACT 2>/dev/null | tar -x -C "$OUT" || git archive gh-pages draft latest versions.json | tar -x -C "$OUT"
rm -rf "$OUT/specification" && (cd "$OUT" && ln -s latest/specification specification && ln -s latest/schemas schemas)

echo "Built $OUT. Serve with: python3 -m http.server 8000 -d $OUT"
