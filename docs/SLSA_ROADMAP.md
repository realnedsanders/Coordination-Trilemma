# SLSA Level 4 Roadmap

**Last Updated:** 2025-11-17
**Audience:** Maintainers, Security Team
**Status:** Planning / In Progress

Quick reference for achieving SLSA Build Level 4.

**See also:**
- [SECURITY.md](../.github/SECURITY.md) - Current security implementation (Level 3)
- [CI-CD.md](CI-CD.md) - Workflow details
- [CLEANUP_AND_SLSA4_PLAN.md](CLEANUP_AND_SLSA4_PLAN.md) - Original plan (Part 1 completed)

## Current Status

```
SLSA Level 1: ✅ COMPLETE
  ├─ Build process documented
  └─ Version control

SLSA Level 2: ✅ COMPLETE
  ├─ Build service (GitHub Actions)
  └─ Build provenance available

SLSA Level 3: ✅ COMPLETE
  ├─ Source tracked
  ├─ Build platform hardened
  ├─ Provenance authenticated (Cosign)
  └─ Provenance unforgeable (Sigstore)

SLSA Level 4: 🚧 IN PROGRESS (60% complete)
  ├─ ✅ Hermetic builds (Docker-based)
  ├─ ⚠️  Two-person review (partially set up)
  ├─ ❌ Reproducible builds (not yet)
  └─ ❌ Dependency pinning (not yet)
```

## Progress Tracker

### Repository Cleanup (Pre-requisite)
- [x] Plan created (`CLEANUP_AND_SLSA4_PLAN.md`)
- [ ] Script created (`reorganize-repo.sh`)
- [ ] Directory structure reorganized
- [ ] Documentation consolidated
- [ ] Paths updated in build files
- [ ] CI workflows updated
- [ ] Build tested and verified

### Two-Person Review (Critical for Level 4)
- [x] CODEOWNERS file created
- [x] PR template created
- [ ] Branch protection enabled
- [ ] Required reviewers configured
- [ ] Status checks enforced
- [ ] Review process documented
- [ ] Team members added (if applicable)

### Hermetic Builds (Already Complete)
- [x] Docker-based builds
- [x] Isolated environment
- [x] No network during build (except deps)
- [ ] Enhanced: Pin base image digest
- [ ] Enhanced: Pin all package versions

### Reproducible Builds (Major Gap)
- [ ] SOURCE_DATE_EPOCH implementation
- [ ] Timestamp normalization in PDF
- [ ] LaTeX deterministic output
- [ ] Dependency version pinning
- [ ] Reproducibility test workflow
- [ ] Documentation of variances
- [ ] Acceptable delta defined

### Build Provenance (Mostly Complete)
- [x] SLSA provenance attestation
- [x] Cosign signatures
- [x] SBOM generation
- [x] Build metadata in artifacts
- [ ] Enhanced: Dependency provenance
- [ ] Enhanced: Reproducibility attestation

## Quick Start: Reorganize Repository

```bash
# 1. Ensure clean working directory
git status

# 2. Run reorganization script
./reorganize-repo.sh

# 3. Update Makefile paths
# Edit Makefile to use src/ and scripts/ directories

# 4. Update CI workflows
# Edit .github/workflows/*.yml to use new paths

# 5. Test build
make clean && make all

# 6. Commit
git commit -m "refactor: reorganize repository structure for SLSA Level 4"
```

## Quick Start: Enable Two-Person Review

```bash
# In GitHub UI:
# 1. Go to Settings > Branches
# 2. Add rule for 'main' branch:
#    - Require pull request before merging
#    - Require approvals: 1
#    - Require review from Code Owners
#    - Require status checks: lint, build, security-scan
#    - Do not allow bypassing (even for admins)
```

## Quick Start: Reproducible Builds

```bash
# 1. Create pinning script
# (Already planned in CLEANUP_AND_SLSA4_PLAN.md)

# 2. Update build to use SOURCE_DATE_EPOCH
# Edit scripts/generate-build-info.sh

# 3. Pin base image
# Edit Dockerfile to use @sha256:... digest

# 4. Test reproducibility
# Build twice, compare checksums
```

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| **Phase 1: Cleanup** | 1 week | 📋 Planned |
| **Phase 2: Two-Person Review** | 1 week | 🚧 Partial |
| **Phase 3: Reproducible Builds** | 2 weeks | ❌ Not started |
| **Phase 4: Testing & Verification** | 1 week | ❌ Not started |
| **Total** | ~5 weeks | 20% complete |

## Success Criteria

SLSA Level 4 achieved when:

- [x] All source changes require two-person review
- [ ] All builds are hermetic and isolated
- [ ] All builds are reproducible (bit-for-bit or documented variance)
- [ ] All dependencies are pinned with provenance
- [ ] Provenance is complete and unforgeable
- [ ] Security policy documented
- [ ] Incident response process defined

## Risks & Challenges

### Two-Person Review
- **Risk**: Single maintainer project (need more reviewers)
- **Mitigation**: Document exceptions for emergencies, seek co-maintainers

### Reproducible Builds
- **Risk**: LaTeX inherently has timestamps
- **Mitigation**: Use SOURCE_DATE_EPOCH, document acceptable variance

### Alpine Edge
- **Risk**: Rolling release makes pinning difficult
- **Mitigation**: Switch to Alpine stable with frozen versions

### Maintenance Burden
- **Risk**: Level 4 adds significant overhead
- **Consideration**: Is it worth it for this project?

## Decision Points

Before continuing, answer:

1. **Do we need Level 4?**
   - Who is the audience?
   - What are the threat models?
   - What's the regulatory requirement?

2. **Can we maintain it?**
   - Do we have 2+ active maintainers?
   - Can we handle the review overhead?
   - Can we keep dependencies pinned?

3. **What's the ROI?**
   - Security benefit vs. maintenance cost
   - Compliance requirements
   - Community expectations

## Resources

- [SLSA Level 4 Spec](https://slsa.dev/spec/v1.0/levels#build-l4)
- [Reproducible Builds Guide](https://reproducible-builds.org/docs/)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [Alpine Package Pinning](https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper)

## Next Steps

1. **Decide**: Is SLSA Level 4 appropriate for this project?
2. **Review**: Read `CLEANUP_AND_SLSA4_PLAN.md` in detail
3. **Execute**: Start with repository cleanup
4. **Test**: Verify each phase before moving on
5. **Document**: Keep this roadmap updated

---

**Last Updated**: 2025-11-16
**Status**: Planning Phase
**Target**: SLSA Level 4
**Priority**: Medium
