# Infrastructure Setup Summary

**Created:** 2025-11-17
**Status:** Ready for implementation

## What Was Created

A complete infrastructure-as-code setup using OpenTofu for the `enlightenment-dev` GitHub organization.

## Files Created

All files are in `/tmp/infrastructure-terraform/` ready to be moved to a new private repository.

### Infrastructure Repository Structure

```text
infrastructure-terraform/
├── .github/workflows/
│   ├── tofu-plan.yml          # Show plan on PRs
│   └── tofu-apply.yml         # Apply on merge to main
├── terraform/
│   ├── organization/
│   │   ├── main.tf            # Org settings (security, defaults)
│   │   ├── teams.tf           # Team definitions
│   │   ├── variables.tf       # Configuration variables
│   │   └── outputs.tf         # Output values
│   └── repositories/
│       └── coordination-trilemma/
│           ├── main.tf              # Repository configuration
│           ├── branch-protection.tf # Branch protection rules
│           ├── teams.tf             # Team permissions
│           ├── variables.tf         # Repo-specific variables
│           └── outputs.tf           # Repo outputs
├── examples/
│   ├── CODEOWNERS             # Example CODEOWNERS file
│   └── dependabot-automerge.yml    # Dependabot auto-merge workflow
├── docs/
│   └── SETUP.md               # Step-by-step setup guide
├── README.md                  # Infrastructure repo documentation
├── .gitignore                 # Git ignore patterns
└── terraform.tfvars.example   # Example configuration file
```

### Main Repository Updates

Files to add to `Coordination-Trilemma` repository:

- `.github/CODEOWNERS` - Code ownership and review requirements
- `.github/workflows/dependabot-automerge.yml` - Auto-merge for Dependabot PRs
- `docs/INFRASTRUCTURE.md` - Infrastructure documentation (already created)

## Key Features

### 1. Multi-Party Review (SLSA Level 4)

- ✅ **2 required approvals** from core-maintainers team
- ✅ **CODEOWNERS** enforces review requirements
- ✅ **Code owner reviews** required for sensitive files
- ✅ **Last push approval** prevents self-approval
- ✅ **Enforce for admins** - no bypassing

### 2. Automated Testing & Deployment

- ✅ **Required status checks** - All CI jobs must pass
- ✅ **Branch must be up to date** before merging
- ✅ **No force pushes** to main branch
- ✅ **Conversation resolution** required

### 3. Dependabot Auto-Merge

- ✅ **Patch/minor updates** auto-merge after 1 hour
- ✅ **Major updates** require manual review
- ✅ **All tests must pass** before merge
- ✅ **Stability window** prevents immediate merges

### 4. Infrastructure as Code

- ✅ **Version controlled** - All settings in git
- ✅ **Auditable** - Full history of changes
- ✅ **Reviewable** - PR workflow for changes
- ✅ **Automated** - GitHub Actions applies changes
- ✅ **State management** - Stored in dedicated branch

### 5. Security

- ✅ **OIDC authentication** - No long-lived tokens
- ✅ **Encrypted state** - GitHub repository encryption
- ✅ **Branch protection** - Prevents unauthorized changes
- ✅ **Audit trail** - All changes logged in git

## Implementation Steps

### Phase 1: Setup Infrastructure Repository

1. Create private `enlightenment-dev/infrastructure-terraform` repo
2. Copy files from `/tmp/infrastructure-terraform/`
3. Create `terraform-state` branch
4. Configure repository secrets
5. Set up branch protection for `terraform-state`

**Time:** ~30 minutes

### Phase 2: Import Existing State

1. Import organization settings
2. Create teams if needed
3. Test plan/apply workflow locally

**Time:** ~30 minutes

### Phase 3: Transfer Main Repository

1. Transfer `Coordination-Trilemma` to `enlightenment-dev`
2. Update documentation references
3. Import repository state into Terraform

**Time:** ~15 minutes

### Phase 4: Apply Infrastructure Policies

1. Apply Terraform to set branch protection
2. Add CODEOWNERS file to main repo
3. Add Dependabot auto-merge workflow
4. Test with a dummy PR

**Time:** ~30 minutes

### Phase 5: Verify & Test

1. Create test PR in infrastructure repo
2. Verify plan workflow works
3. Merge and verify apply works
4. Create test PR in main repo
5. Verify reviews required, auto-merge works

**Time:** ~30 minutes

**Total estimated time:** ~2.5 hours

## Configuration Details

### Organization Settings

- **Default permission:** Read
- **Members can create repos:** No (only via Terraform)
- **Commit signoff:** Required
- **Advanced security:** Enabled for new repos
- **Dependabot alerts:** Enabled
- **Secret scanning:** Enabled with push protection

### Branch Protection (main)

- **Required reviews:** 2 from core-maintainers
- **Code owner reviews:** Required
- **Dismiss stale reviews:** Yes
- **Require branch up to date:** Yes
- **Required checks:** All CI jobs
- **Enforce for admins:** Yes
- **No force pushes:** Yes
- **No deletions:** Yes

### Teams

**core-maintainers:**

- Admin access to all repos
- Can approve infrastructure changes
- Current members: realnedsanders (update in variables.tf)

**contributors:** (disabled by default)

- Write access when enabled
- For trusted external contributors

**community:** (disabled by default)

- Read access when enabled
- For community participants

### Dependabot Auto-Merge Rules

**Auto-merge if:**

- ✅ PR is from Dependabot
- ✅ Update type is patch or minor
- ✅ All required checks pass
- ✅ PR is at least 1 hour old

**Manual review required for:**

- ❌ Major version updates
- ❌ Failed status checks
- ❌ Security vulnerabilities introduced

## State Management

### State Storage

- **Location:** `terraform-state` branch in infrastructure repo
- **Format:** Standard Terraform JSON state files
- **Encryption:** GitHub repository encryption at rest
- **Access:** GitHub Actions with OIDC only

### State Structure

```text
terraform-state/
├── organization.tfstate
└── repositories/
    └── coordination-trilemma.tfstate
```

### State Locking

- **Mechanism:** GitHub branch protection + workflow concurrency
- **Prevents:** Concurrent applies
- **Recovery:** Automatic via git history

## Maintenance

### Adding Team Members

```bash
cd terraform/organization
vi teams.tf  # Add to core_maintainers list
# PR, review, merge
```

### Updating Branch Protection

```bash
cd terraform/repositories/coordination-trilemma
vi branch-protection.tf  # Change required_approving_review_count, etc.
# PR, review, merge
```

### Adding New Repositories

```bash
cd terraform/repositories
cp -r coordination-trilemma new-repo
cd new-repo
# Edit main.tf, branch-protection.tf
# PR, review, merge
```

## Security Considerations

### Sensitive Data

- Never commit `.tfstate` to main branch
- Never commit GitHub tokens
- Use repository secrets for emails
- Mark sensitive variables with `sensitive = true`

### Access Control

- Infrastructure repo is private
- Only core-maintainers can merge
- All changes require 2 reviews
- OIDC authentication (no stored credentials)

### Audit Trail

- All changes are git commits
- PRs show plan before apply
- State history in `terraform-state` branch
- GitHub audit log for access

## OpenTofu vs Terraform

**Why OpenTofu:**

- ✅ Fully open source (MPL 2.0)
- ✅ Drop-in replacement for Terraform
- ✅ Community-driven governance
- ✅ No license restrictions
- ✅ Better for academic/research projects

**Compatibility:**

- Uses same HCL syntax
- Compatible with Terraform providers
- Can migrate from Terraform seamlessly
- Same commands (`tofu` instead of `terraform`)

## Next Steps

1. **Review configuration files** in `/tmp/infrastructure-terraform/`
2. **Update variables** in `terraform.tfvars.example`
3. **Follow setup guide** in `docs/SETUP.md`
4. **Test locally** before applying in CI
5. **Transfer repository** to org
6. **Apply policies** via Terraform

## Questions?

Refer to:

- [INFRASTRUCTURE.md](INFRASTRUCTURE.md) - Architecture overview
- [/tmp/infrastructure-terraform/docs/SETUP.md](file:///tmp/infrastructure-terraform/docs/SETUP.md) - Setup guide
- [/tmp/infrastructure-terraform/README.md](file:///tmp/infrastructure-terraform/README.md) - Usage guide

## Resources

- [OpenTofu Documentation](https://opentofu.org/docs/)
- [GitHub Provider Docs](https://registry.terraform.io/providers/integrations/github/latest/docs)
- [GitHub OIDC Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [SLSA Level 4 Requirements](https://slsa.dev/spec/v1.0/levels#build-l4)
