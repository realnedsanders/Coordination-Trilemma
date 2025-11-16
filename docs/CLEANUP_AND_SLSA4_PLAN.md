# Repository Cleanup & SLSA Level 4 Plan

This document outlines the plan to reorganize the repository for better clarity and achieve SLSA Build Level 4.

---

## Part 1: Repository Cleanup

### Current Issues

1. **Root directory clutter**: 28+ files at root level
2. **Multiple README files**: README.md, LATEX_README.md, QUICKSTART.md, DOCKER_SETUP.md
3. **Duplicate files**: Both .md and .tex versions of appendices
4. **Scripts scattered**: Shell scripts mixed with source files
5. **Working drafts visible**: Draft content in main tree
6. **No clear separation**: Source, docs, scripts, and build configs all mixed

### Proposed Directory Structure

```
coordination-trilemma/
├── README.md                          # Main README (consolidated)
├── SECURITY.md                        # Security documentation
├── LICENSE                            # License file
├── Makefile                           # Top-level build automation
├── Dockerfile                         # Container definition
│
├── docs/                              # All documentation
│   ├── quickstart.md                  # Getting started guide
│   ├── docker-setup.md                # Docker-specific docs
│   ├── latex-guide.md                 # LaTeX compilation guide
│   ├── security-verification.md       # How to verify signatures
│   └── contributing.md                # Contribution guidelines
│
├── src/                               # LaTeX source files
│   ├── main.tex                       # Main document
│   ├── main-article.tex               # Article body
│   ├── glossary.tex                   # Glossary
│   ├── references.bib                 # Bibliography
│   └── appendices/                    # Appendices
│       ├── appendix-a.tex
│       ├── appendix-b.tex
│       ├── appendix-c.tex
│       └── appendix-d.tex
│
├── scripts/                           # Build and utility scripts
│   ├── generate-build-info.sh         # Build provenance generation
│   ├── verify-signatures.sh           # Security verification
│   └── pin-dependencies.sh            # Pin dependency versions (new)
│
├── .github/                           # GitHub-specific files
│   ├── workflows/                     # CI/CD workflows
│   │   ├── ci.yml                     # Main CI pipeline
│   │   ├── docker-build.yml           # Docker image build
│   │   └── sign-pdf.yml               # PDF signing
│   ├── CODEOWNERS                     # Code ownership (new for Level 4)
│   └── PULL_REQUEST_TEMPLATE.md       # PR template (new)
│
├── build/                             # Build outputs (gitignored)
│   ├── build-info.tex                 # Generated build metadata
│   └── *.aux, *.log, etc.             # LaTeX artifacts
│
├── web/                               # GitHub Pages content
│   └── index.html                     # Landing page
│
└── drafts/                            # Private drafts (gitignored)
    ├── working/                       # Work in progress
    └── archive/                       # Old versions
```

### Cleanup Tasks

#### Phase 1: Consolidate Documentation
- [ ] Merge all README files into single README.md with sections
- [ ] Move detailed guides to `docs/` directory
- [ ] Update all internal links
- [ ] Create docs/README.md as index

#### Phase 2: Reorganize Source Files
- [ ] Create `src/` directory
- [ ] Move all .tex files to `src/`
- [ ] Create `src/appendices/` subdirectory
- [ ] Update Makefile paths
- [ ] Update CI workflow paths

#### Phase 3: Scripts Organization
- [ ] Create `scripts/` directory
- [ ] Move all .sh files to `scripts/`
- [ ] Update Makefile to reference new paths
- [ ] Update CI workflows
- [ ] Make all scripts executable

#### Phase 4: Web Content
- [ ] Create `web/` directory
- [ ] Move index.html to `web/`
- [ ] Update GitHub Pages workflow

#### Phase 5: Build Artifacts
- [ ] Create `build/` directory
- [ ] Update Makefile to output to `build/`
- [ ] Update .gitignore for `build/`
- [ ] Update CI to handle new structure

#### Phase 6: Clean Up Duplicates
- [ ] Remove .md versions of appendices (keep .tex)
- [ ] Archive or remove "working drafts" and "future plans" directories
- [ ] Document what was removed in CHANGELOG.md

---

## Part 2: SLSA Level 4 Implementation

### Current Status: SLSA Level 3 ✅

We have:
- ✅ Version controlled source
- ✅ Build service (GitHub Actions)
- ✅ Build as code (versioned workflows)
- ✅ Authenticated provenance (Cosign signatures)
- ✅ Unforgeable provenance (Sigstore transparency)
- ✅ Complete provenance (SLSA attestations)

### SLSA Level 4 Requirements

#### 1. Two-Person Review ⚠️

**Current state**: No enforcement
**Required**: All changes reviewed by another trusted person

**Implementation:**

##### A. Branch Protection Rules
```yaml
# .github/branch-protection.yml (conceptual - set in repo settings)
main:
  required_reviewers: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  required_status_checks:
    - lint
    - build
    - security-scan
  enforce_admins: true
  restrict_pushes: true
```

**Tasks:**
- [ ] Enable branch protection on `main`
- [ ] Require at least 1 approval
- [ ] Require review from code owners
- [ ] Dismiss stale reviews on update
- [ ] Require status checks to pass
- [ ] Enforce for administrators

##### B. CODEOWNERS File
```
# .github/CODEOWNERS
# All files require review from core team
* @realnedsanders/core-team

# Security-sensitive files require additional review
/Dockerfile @realnedsanders/security-team
/.github/workflows/ @realnedsanders/security-team
/scripts/ @realnedsanders/security-team
SECURITY.md @realnedsanders/security-team
```

**Tasks:**
- [ ] Create CODEOWNERS file
- [ ] Define team structure
- [ ] Assign ownership

##### C. Pull Request Template
**Tasks:**
- [ ] Create PR template
- [ ] Require security checklist
- [ ] Require testing checklist
- [ ] Require documentation updates

#### 2. Hermetic Builds ✅

**Current state**: ✅ Already hermetic (Docker-based)
- Builds run in isolated containers
- No network access during build (except package downloads)
- Reproducible environment

**Improvements:**
- [ ] Pin Alpine base image to specific digest
- [ ] Pin all package versions
- [ ] Cache package lists for reproducibility

#### 3. Reproducible Builds ⚠️

**Current state**: Partially reproducible
- ✅ Source code versioned
- ✅ Build scripts versioned
- ⚠️ Timestamps vary
- ⚠️ Alpine edge packages change

**Implementation:**

##### A. Use SOURCE_DATE_EPOCH
```bash
# In generate-build-info.sh
export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
```

**Tasks:**
- [ ] Set SOURCE_DATE_EPOCH from git commit timestamp
- [ ] Configure pdflatex to use SOURCE_DATE_EPOCH
- [ ] Normalize all timestamps

##### B. Pin All Dependencies
Create `scripts/pin-dependencies.sh`:
```bash
#!/bin/bash
# Pin Alpine packages to specific versions
# Output: Dockerfile.pinned with frozen versions
```

**Tasks:**
- [ ] Create dependency pinning script
- [ ] Generate Dockerfile with pinned versions
- [ ] Document pinning process
- [ ] Automate version updates

##### C. Reproducibility Testing
Create `.github/workflows/reproducibility-test.yml`:
```yaml
# Build twice and compare outputs
# Ensures bit-for-bit reproducibility
```

**Tasks:**
- [ ] Create reproducibility test workflow
- [ ] Build PDF twice from same commit
- [ ] Compare checksums
- [ ] Report on differences

#### 4. Build Provenance Enhancements

**Additional attestations:**
- [ ] Add vulnerability disclosure policy
- [ ] Document incident response process
- [ ] Add security contacts
- [ ] Create security.txt file

---

## Implementation Timeline

### Week 1: Repository Cleanup
- **Day 1-2**: Consolidate documentation
- **Day 3-4**: Reorganize directory structure
- **Day 5**: Update all references and test builds

### Week 2: Two-Person Review
- **Day 1-2**: Set up branch protection
- **Day 3**: Create CODEOWNERS and templates
- **Day 4-5**: Document review process

### Week 3: Reproducible Builds
- **Day 1-2**: Implement SOURCE_DATE_EPOCH
- **Day 3-4**: Pin dependencies
- **Day 5**: Create reproducibility tests

### Week 4: Testing & Documentation
- **Day 1-2**: End-to-end testing
- **Day 3-4**: Update all documentation
- **Day 5**: Final SLSA Level 4 verification

---

## SLSA Level 4 Checklist

### Build Platform Requirements
- [x] Builds run on GitHub Actions
- [x] Build service is hardened (GitHub-managed)
- [x] Build service is isolated
- [ ] Build service ensures hermetic builds
- [ ] Build service provides build-as-code

### Source Requirements
- [x] Version controlled (Git)
- [ ] Two-person reviewed
- [ ] All changes reviewed before merge

### Build Process
- [x] Scripted build
- [x] Build service generates provenance
- [x] Provenance is unforgeable
- [x] Provenance is authenticated
- [ ] Provenance includes all dependencies
- [ ] Dependencies are pinned

### Provenance Requirements
- [x] Cryptographically signed
- [x] Service-generated (not self-attested)
- [x] Non-falsifiable
- [x] Complete (all build inputs)
- [ ] Reproducible (bit-for-bit)

### Additional Requirements
- [ ] Two-person review documented
- [ ] Review process enforced
- [ ] Build hermiticity verified
- [ ] Reproducibility tested
- [ ] Security disclosure policy

---

## Benefits of SLSA Level 4

1. **Highest trust level**: Maximum confidence in artifact integrity
2. **Insider threat protection**: Requires collusion to compromise
3. **Regulatory compliance**: Meets strictest supply chain requirements
4. **Reproducible audits**: Anyone can verify builds
5. **Industry leadership**: Few projects achieve Level 4

---

## Questions to Answer

1. **Team structure**: Do we have multiple maintainers for two-person review?
2. **Review SLA**: What's acceptable review turnaround time?
3. **Emergency process**: How to handle critical security fixes?
4. **Reproducibility tolerance**: Acceptable delta for "close enough"?
5. **Maintenance burden**: Is Level 4 worth the overhead for this project?

---

## Resources

- [SLSA Framework](https://slsa.dev/)
- [SLSA Level 4 Requirements](https://slsa.dev/spec/v1.0/levels#build-l4)
- [Reproducible Builds](https://reproducible-builds.org/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
