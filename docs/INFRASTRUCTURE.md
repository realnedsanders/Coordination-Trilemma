# Infrastructure as Code

**Last Updated:** 2025-11-17
**Audience:** Maintainers
**Status:** Planning

This document describes the infrastructure-as-code setup for the Coordination Trilemma project.

**See also:**

- [SLSA_ROADMAP.md](SLSA_ROADMAP.md) - Path to SLSA Level 4
- [CI-CD.md](CI-CD.md) - Workflow architecture
- [.github/SECURITY.md](../.github/SECURITY.md) - Security documentation

## Overview

All GitHub infrastructure (repository settings, branch protection, teams, permissions) is managed as
code using OpenTofu (open source Terraform fork) in a private repository.

**Benefits:**

- ✅ Version controlled and auditable
- ✅ Multi-party review required for all infrastructure changes
- ✅ Reproducible and documented
- ✅ Meets SLSA Level 4 requirements
- ✅ No manual clicking in GitHub UI

## Architecture

### Repositories

**Main repository:** `enlightenment-dev/Coordination-Trilemma`

- Public repository containing the paper and build infrastructure
- Managed via Terraform in the infrastructure repo
- Branch protection enforced via code

**Infrastructure repository:** `enlightenment-dev/infrastructure-terraform` (private)

- Private repository containing all OpenTofu configurations
- State stored in dedicated `terraform-state` branch
- Changes applied automatically on merge to `main`

### Repository Structure

```text
enlightenment-dev/infrastructure-terraform/
├── README.md
├── .github/
│   └── workflows/
│       ├── tofu-plan.yml        # PR: Show plan
│       └── tofu-apply.yml       # Main: Apply changes
├── terraform/
│   ├── organization/
│   │   ├── main.tf              # Org-level settings
│   │   ├── teams.tf             # Team definitions
│   │   └── variables.tf
│   ├── repositories/
│   │   └── coordination-trilemma/
│   │       ├── main.tf          # Repo settings
│   │       ├── branch-protection.tf
│   │       ├── teams.tf         # Repo team permissions
│   │       └── variables.tf
│   └── modules/                 # Reusable modules
│       ├── repository/
│       └── team/
└── docs/
    └── USAGE.md
```

## Configuration

### Teams

**core-maintainers**

- Full admin access to repositories
- Can approve infrastructure changes
- Required for all PRs (2 reviews minimum for SLSA L4)

**contributors**

- Write access to repositories
- Can create PRs and issues
- Cannot merge without review

**community**

- Read access
- Can create issues and participate in discussions

### Branch Protection Rules

**Main repository (`main` branch):**

```hcl
Required:
- 2 approving reviews from core-maintainers
- All status checks must pass:
  - Build Docker Images
  - LaTeX Build & Deploy (build job)
  - Code Quality & Security Scanning (all jobs)
- Conversation resolution required
- No force pushes
- No deletions
- Enforce for administrators

Auto-merge allowed:
- Dependabot PRs that pass all tests
- Only for patch/minor version updates
- Major updates require manual review
```

### Dependabot Auto-Merge

Dependabot PRs are automatically merged if:

1. ✅ All required status checks pass
2. ✅ Update is patch or minor version (not major)
3. ✅ No known security vulnerabilities introduced
4. ⏱️ PR is at least 1 hour old (stability window)

Major version updates require manual review by core-maintainers.

## State Management

### State Storage

State is stored in the `terraform-state` branch of the infrastructure repo:

```text
terraform-state/
├── organization.tfstate
└── repositories/
    └── coordination-trilemma.tfstate
```

**State file handling:**

- Encrypted at rest (GitHub repository encryption)
- Only accessible via GitHub Actions with OIDC
- State locking via GitHub branch protection (prevents concurrent applies)
- Full audit trail via git history

### State Locking

Branch protection on `terraform-state` prevents concurrent modifications:

- Only GitHub Actions can push to `terraform-state`
- Workflow uses `concurrency` group to serialize applies
- Failed applies don't update state

## Workflows

### Pull Request Workflow

1. Developer opens PR to `infrastructure-terraform` main branch
2. `tofu-plan.yml` workflow triggers
3. Workflow checks out code and state
4. Runs `tofu plan` and posts results as PR comment
5. Core maintainer reviews plan and code changes
6. Second maintainer approves (required for merge)
7. PR merges to main

### Apply Workflow

1. Merge to `main` triggers `tofu-apply.yml`
2. Workflow checks out code and state
3. Runs `tofu apply` with auto-approve
4. Updates state file in `terraform-state` branch
5. Posts summary to commit status

### Security

**OIDC Authentication:**

- No long-lived GitHub tokens stored
- Workflows authenticate via GitHub OIDC provider
- Temporary credentials issued per workflow run
- Scoped to minimum required permissions

**Permissions:**

```yaml
permissions:
  contents: write       # Update state branch
  pull-requests: write  # Comment on PRs
  id-token: write      # OIDC authentication
```

## Migration Plan

### Phase 1: Initial Setup (This PR)

- [ ] Create `enlightenment-dev/infrastructure-terraform` private repo
- [ ] Set up OpenTofu configurations
- [ ] Create `terraform-state` branch with protection
- [ ] Configure GitHub Actions workflows
- [ ] Import existing repository state
- [ ] Test plan/apply cycle

### Phase 2: Repository Transfer

- [ ] Transfer `realnedsanders/Coordination-Trilemma` → `enlightenment-dev/Coordination-Trilemma`
- [ ] Update all references in documentation
- [ ] Update GitHub Actions secrets if needed
- [ ] Verify CI/CD pipelines work post-transfer

### Phase 3: Enable Policies

- [ ] Apply branch protection rules via Terraform
- [ ] Enable required reviews (2 minimum)
- [ ] Set up Dependabot auto-merge workflow
- [ ] Test full workflow with dummy PR

### Phase 4: Team Expansion (Future)

- [ ] Add additional maintainers to core-maintainers team
- [ ] Create contributor team for trusted contributors
- [ ] Set up community team for broader participation

## Usage

### Making Infrastructure Changes

1. Clone `infrastructure-terraform` repo
2. Create feature branch
3. Edit `.tf` files
4. Commit and push
5. Open PR
6. Review plan output
7. Get 2 approvals
8. Merge (auto-applies)

### Adding a New Repository

```bash
cd terraform/repositories
cp -r coordination-trilemma new-repo-name
# Edit main.tf with new repo settings
git add .
git commit -m "feat: add new-repo-name"
git push origin feature/new-repo
```

### Updating Branch Protection

Edit `terraform/repositories/coordination-trilemma/branch-protection.tf`:

```hcl
required_approving_review_count = 3  # Increase from 2
```

Commit, PR, review, merge.

## Verification

### Verify Configuration

```bash
cd terraform/repositories/coordination-trilemma
tofu plan
```

### Verify State

```bash
git checkout terraform-state
cat repositories/coordination-trilemma.tfstate | jq '.resources[] | .type'
```

### Verify Applied Settings

- Go to repository Settings → Branches → Branch protection rules
- Verify rules match Terraform configuration
- Check Teams & access match team definitions

## Troubleshooting

### State Conflicts

If concurrent applies conflict:

```bash
git checkout terraform-state
git pull origin terraform-state
git checkout main
tofu refresh
tofu plan
```

### Failed Apply

1. Check workflow logs for error
2. Fix issue in new PR
3. State remains at last successful apply
4. No manual intervention needed

### Manual State Recovery

If state branch is corrupted:

1. Check out last known good state commit
2. Create new branch from that commit
3. Force push to `terraform-state` (emergency only)
4. Re-run apply workflow

## Security Considerations

### Sensitive Data

- Never commit GitHub tokens or secrets to Terraform files
- Use `sensitive = true` for any sensitive variables
- Rotate OIDC permissions regularly

### Access Control

- Infrastructure repo is private
- Only core-maintainers can merge to `main`
- All changes require 2 reviews minimum
- GitHub Actions uses OIDC (no stored secrets)

### Audit Trail

- All infrastructure changes are git commits
- PRs show plan before apply
- State history tracked in `terraform-state` branch
- GitHub audit log shows all access

## References

- [OpenTofu Documentation](https://opentofu.org/docs/)
- [Terraform GitHub Provider](https://registry.terraform.io/providers/integrations/github/latest/docs)
- [GitHub OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [SLSA Level 4 Requirements](https://slsa.dev/spec/v1.0/levels#build-l4)

## Questions?

Open an issue in the infrastructure repo with `[question]` tag.
