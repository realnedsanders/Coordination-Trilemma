#!/usr/bin/env bash
# Repository Reorganization Script
# This script reorganizes the Coordination Trilemma repository
# according to the CLEANUP_AND_SLSA4_PLAN.md
#
# WARNING: This script will move files around. Make sure you have
# committed all changes and have a backup before running!

set -e

echo "🧹 Coordination Trilemma Repository Reorganization"
echo "=================================================="
echo ""

# Safety check
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: Working directory is not clean!"
  echo "Please commit or stash your changes before running this script."
  exit 1
fi

echo "✅ Working directory is clean"
echo ""

# Confirm before proceeding
read -p "This will reorganize the repository structure. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 0
fi

echo ""
echo "Step 1: Creating new directory structure..."

# Create new directories
mkdir -p docs
mkdir -p src/appendices
mkdir -p scripts
mkdir -p build
mkdir -p web

echo "  ✅ Directories created"

echo ""
echo "Step 2: Moving LaTeX source files..."

# Move main LaTeX files to src/
git mv main.tex src/
git mv main-article.tex src/
git mv glossary.tex src/
git mv references.bib src/

# Move appendices
git mv appendix-a.tex src/appendices/
git mv appendix-b.tex src/appendices/
git mv appendix-c.tex src/appendices/
git mv appendix-d.tex src/appendices/

echo "  ✅ LaTeX files moved to src/"

echo ""
echo "Step 3: Moving scripts..."

git mv generate-build-info.sh scripts/
git mv verify-signatures.sh scripts/

echo "  ✅ Scripts moved to scripts/"

echo ""
echo "Step 4: Consolidating documentation..."

# Move specific docs to docs/
if [ -f "QUICKSTART.md" ]; then
  git mv QUICKSTART.md docs/quickstart.md
fi

if [ -f "LATEX_README.md" ]; then
  git mv LATEX_README.md docs/latex-guide.md
fi

if [ -f "DOCKER_SETUP.md" ]; then
  git mv DOCKER_SETUP.md docs/docker-setup.md
fi

echo "  ✅ Documentation organized"

echo ""
echo "Step 5: Moving web content..."

git mv index.html web/

echo "  ✅ Web content moved to web/"

echo ""
echo "Step 7: Updating .gitignore..."

cat >>.gitignore <<'EOF'

# Build directory
build/

# Drafts (not tracked)
drafts/
EOF

echo "  ✅ .gitignore updated"

echo ""
echo "Step 8: Moving drafts to untracked directory..."

# Move working drafts to untracked location
if [ -d "working drafts" ]; then
  mkdir -p drafts/working
  mv "working drafts"/* drafts/working/ 2>/dev/null || true
  rmdir "working drafts" 2>/dev/null || true
fi

if [ -d "future plans" ]; then
  mkdir -p drafts/archive
  mv "future plans"/* drafts/archive/ 2>/dev/null || true
  rmdir "future plans" 2>/dev/null || true
fi

echo "  ✅ Drafts moved to untracked directory"

echo ""
echo "=================================================="
echo "✅ Repository reorganization complete!"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git status"
echo "  2. Update Makefile paths (see CLEANUP_AND_SLSA4_PLAN.md)"
echo "  3. Update CI workflow paths"
echo "  4. Test the build: make all"
echo "  5. Commit changes: git commit -m 'Reorganize repository structure'"
echo ""
echo "See CLEANUP_AND_SLSA4_PLAN.md for detailed next steps."
