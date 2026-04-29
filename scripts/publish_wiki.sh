#!/usr/bin/env bash
# Publish docs/wiki/ → the GitHub Wiki repo (`<repo>.wiki.git`).
#
# GitHub Wikis are a separate git repo, so checking files into docs/wiki/
# never reaches the rendered Wiki tab on its own. This script mirrors the
# directory in, with a few transformations:
#
#   * docs/wiki/README.md  →  Home.md     (the Wiki landing page)
#   * everything else is copied at the same path
#   * _Sidebar.md is generated from the wiki index so the left rail
#     mirrors docs/wiki/README.md
#
# Local usage (need wiki write access):
#
#   ./scripts/publish_wiki.sh                       # uses default remote
#   WIKI_REMOTE=git@github.com:foo/bar.wiki.git ./scripts/publish_wiki.sh
#
# CI usage: see .github/workflows/wiki.yml — run on push to main when
# docs/wiki/** changes.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_SRC="$REPO_ROOT/docs/wiki"
WIKI_REMOTE="${WIKI_REMOTE:-git@github.com:knowledgestack/ks-cookbook.wiki.git}"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "→ cloning $WIKI_REMOTE"
if ! git clone --depth=1 "$WIKI_REMOTE" "$WORK_DIR/wiki" 2>/dev/null; then
    # Wiki repo doesn't exist yet — initialize it locally.
    echo "  (wiki empty / not yet initialized — creating fresh)"
    mkdir -p "$WORK_DIR/wiki"
    (cd "$WORK_DIR/wiki" && git init -q -b master && git remote add origin "$WIKI_REMOTE")
fi

echo "→ syncing files from $WIKI_SRC"
cd "$WORK_DIR/wiki"
# Wipe everything tracked except .git so deletions in source propagate.
find . -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +

# Copy with rsync-style cp. Preserve subdirectories.
cp -R "$WIKI_SRC/." .

# Promote README.md → Home.md (GitHub Wiki landing page convention).
if [ -f README.md ]; then
    mv README.md Home.md
fi

# Generate _Sidebar.md from Home.md headings + top-level pages.
python3 "$REPO_ROOT/scripts/build_wiki_sidebar.py" --root . --out _Sidebar.md

git add -A
if git diff --cached --quiet; then
    echo "→ no changes; wiki already up to date"
    exit 0
fi

git -c user.name="ks-cookbook bot" -c user.email="bot@knowledgestack.ai" \
    commit -m "wiki: sync from main ($(cd "$REPO_ROOT" && git rev-parse --short HEAD))"
echo "→ pushing"
git push origin HEAD:master
echo "✓ wiki published"
