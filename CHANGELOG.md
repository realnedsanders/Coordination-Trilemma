# Changelog

All notable changes to the Coordination Trilemma project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for infrastructure, though the paper itself follows academic versioning.

## [Unreleased]

### Documentation
- Added CONTRIBUTING.md with comprehensive contribution guidelines
- Added CHANGELOG.md to track project changes
- Updated all documentation with "Last Updated" dates and audience labels
- Fixed outdated file paths in latex-guide.md, docker-setup.md, quickstart.md
- Fixed Docker image size references (custom Alpine ~500MB-1GB vs full TeXLive ~4-5GB)
- Marked CLEANUP_AND_SLSA4_PLAN.md as completed for Part 1

## [2025-11-17] - Build System & CI/CD Improvements

### Added
- Git to LaTeX Docker image for accurate build provenance
- Automatic CI environment detection in Makefile (uses local compilation when inside container)
- Full git history checkout in CI for accurate commit information
- Git safe directory configuration for containers

### Fixed
- Build provenance showing "unknown-dirty" due to missing git in container
- Docker-in-Docker issue in CI (Makefile now detects GitHub Actions)
- Double workflow trigger when Dockerfile and other files change simultaneously
- Sign and deploy jobs being skipped on workflow_run triggers
- Workflow conditions now handle both push and workflow_run event types

### Changed
- LaTeX build workflow now signs PDF before deployment (not after)
- Deploy workflow now publishes signed PDFs to enlightenment.dev
- Deprecated separate sign-pdf.yml workflow (signing integrated into main workflow)
- Path filters optimized to prevent unnecessary workflow runs

## [2025-11-16] - Repository Reorganization

### Added
- Custom Alpine-based LaTeX Docker image (~500MB-1GB vs ~4-5GB full TeXLive)
- Custom security tools Docker image (~50-100MB with Cosign)
- Comprehensive documentation structure in docs/ directory
- Web landing page for GitHub Pages
- Build provenance generation script
- Signature verification script
- SLSA Level 3 compliance with signed artifacts

### Changed
- **BREAKING:** Reorganized repository structure:
  - LaTeX sources moved to `src/tex/`
  - Documentation consolidated in `docs/`
  - Scripts moved to `scripts/`
  - Web content in `web/`
  - Build outputs to `build/` (gitignored)
- README.md now focuses on paper content rather than build instructions
- Technical documentation moved to docs/BUILD.md

### Infrastructure
- Makefile updated for new directory structure
- CI workflows updated for new paths
- Docker images automatically built and signed on changes
- GitHub Pages deployment for PDF at enlightenment.dev

## [2025-11-13] - Initial Public Release

### Added
- LaTeX source for Coordination Trilemma paper
- Main article content with formal proofs
- Four appendices with detailed analysis
- Bibliography with references
- Basic Makefile for building
- Docker-based build system
- GitHub Actions CI/CD
- Security documentation
- SLSA provenance attestations

### Paper Content
- Formal definition of the Coordination Trilemma
- Proofs of impossibility for enforcement-based systems
- Analysis of voluntary coordination requirements
- Metaphysical implications of the trilemma
- Contemporary urgency arguments
- Practical implementation challenges

---

## Version Numbering

**Infrastructure/Build System:** Semantic Versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking changes to build system or structure
- MINOR: New features, workflows, or non-breaking improvements
- PATCH: Bug fixes, documentation updates

**Paper Content:** Academic versioning
- Major revisions tracked by git tags (v1.0, v2.0, etc.)
- Minor corrections tracked in git history
- Published versions have SLSA provenance with commit hash

## Maintaining This Changelog

### When to Update
- Before merging PRs that change functionality
- After major milestones or releases
- When deprecating features or making breaking changes

### Categories
- **Added** - New features, content, or documentation
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements or fixes

### Links
- Repository: https://github.com/realnedsanders/Coordination-Trilemma
- Published PDF: https://enlightenment.dev
- Issues: https://github.com/realnedsanders/Coordination-Trilemma/issues

---

[Unreleased]: https://github.com/realnedsanders/Coordination-Trilemma/compare/main...HEAD
