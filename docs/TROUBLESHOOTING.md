# Troubleshooting Guide

**Last Updated:** 2025-11-17
**Audience:** All Users

Common issues and solutions for building the Coordination Trilemma paper.

## Quick Diagnostics

```bash
# Check Docker is working
docker --version
docker ps

# Check git is working
git status

# Clean build test
make cleanall
make

# Check for errors
cat src/tex/*.log | grep -i error
```

## Build Issues

### Error: "docker: command not found"

**Cause:** Docker is not installed or not in PATH.

**Solution:**
```bash
# macOS
brew install --cask docker
# Then open Docker Desktop

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker

# Windows
# Download Docker Desktop from docker.com
```

**Verify:**
```bash
docker --version
docker ps
```

### Error: "Cannot connect to Docker daemon"

**Cause:** Docker daemon is not running.

**Solution:**
```bash
# macOS/Windows: Open Docker Desktop application

# Linux:
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker ps
```

### Error: "permission denied while trying to connect to Docker"

**Cause:** User not in docker group (Linux).

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker ps
```

### Error: "make: docker: No such file or directory"

**Cause:** Running in CI container trying to use Docker (Docker-in-Docker issue).

**Solution:** This is handled automatically by the Makefile when `GITHUB_ACTIONS` env var is set. If running locally in a container:

```bash
# Use local LaTeX instead
make local
```

### Error: "unknown-dirty" in PDF build info

**Cause:** Git not available in container OR git ownership issues.

**Solution:**
```bash
# If building locally, ensure git is installed
git --version

# If in Docker, the image should include git
# Check image has git:
docker run --rm ghcr.io/realnedsanders/coordination-trilemma/latex:latest git --version

# If git ownership issues:
git config --global --add safe.directory "$(pwd)"
```

### Error: "File not found" or wrong paths

**Cause:** Running from wrong directory or using outdated paths.

**Solution:**
```bash
# Always run make from repository root
cd /path/to/Coordination-Trilemma
make

# LaTeX sources are in src/tex/
ls src/tex/

# Output PDF is at root
ls main.pdf
```

### PDF not generating

**Cause:** LaTeX compilation errors.

**Solution:**
```bash
# Check the logs
cat src/tex/main.log | grep -i error

# Common issues:
# 1. Missing bibliography - check src/tex/references.bib exists
# 2. Missing packages - use full TeXLive image:
DOCKER_IMAGE=texlive/texlive:latest make

# 3. Syntax errors - check .tex files for unclosed braces
```

### Bibliography not appearing

**Cause:** BibTeX not processing correctly.

**Solution:**
```bash
# Full clean build
make cleanall
make

# Check bibliography file exists
ls -la src/tex/references.bib

# Check for BibTeX errors
cat src/tex/main.blg
```

### Citations showing as [?]

**Cause:** Need multiple LaTeX passes for cross-references.

**Solution:**
```bash
# Make runs pdflatex 3 times automatically
# If still broken:
make cleanall
make
```

## Docker Image Issues

### Image pull failing

**Cause:** Network issues or registry problems.

**Solution:**
```bash
# Check network
ping ghcr.io

# Try pulling manually
docker pull ghcr.io/realnedsanders/coordination-trilemma/latex:latest

# If still failing, use full TeXLive as fallback
docker pull texlive/texlive:latest
DOCKER_IMAGE=texlive/texlive:latest make
```

### "Package X not found" error

**Cause:** Custom Alpine image doesn't include all packages.

**Solution:**
```bash
# Use full TeXLive image
DOCKER_IMAGE=texlive/texlive:latest make

# Or add package to docker/Dockerfile.latex and rebuild
```

### Files owned by root after Docker build

**Cause:** Docker runs as root by default.

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or configure Makefile to run as your user (see BUILD.md)
```

### Disk space issues

**Cause:** Docker images take significant space.

**Solution:**
```bash
# Check usage
docker system df

# Clean up old images
docker system prune -a

# Remove specific image
docker rmi ghcr.io/realnedsanders/coordination-trilemma/latex:latest
# Then pull fresh
make docker-pull
```

## Git & Provenance Issues

### "fatal: detected dubious ownership in repository"

**Cause:** Git ownership mismatch (common in containers).

**Solution:**
```bash
# Add safe directory
git config --global --add safe.directory "$(pwd)"

# Or in container
git config --global --add safe.directory /workdir
```

### Build info shows wrong commit

**Cause:** Shallow git clone or detached HEAD.

**Solution:**
```bash
# Ensure full clone
git fetch --unshallow

# Check current commit
git log -1

# Rebuild
make cleanall && make
```

### Build info shows "dirty" when working tree is clean

**Cause:** Untracked files or git index issues.

**Solution:**
```bash
# Check status
git status

# Reset index if needed
git reset

# Clean untracked files (careful!)
git clean -fd

# Rebuild
make cleanall && make
```

## Signature Verification Issues

### "cosign: command not found"

**Cause:** Cosign not installed.

**Solution:**
```bash
# macOS
brew install cosign

# Linux
# See https://docs.sigstore.dev/cosign/installation/

# Verify
cosign version
```

### Signature verification fails

**Cause:** Various - outdated signature, wrong file, network issues.

**Solution:**
```bash
# Download fresh copies
curl -O https://enlightenment.dev/main.pdf
curl -O https://enlightenment.dev/main.pdf.cosign.bundle

# Verify with correct parameters
cosign verify-blob --bundle main.pdf.cosign.bundle \
  --certificate-identity-regexp="^https://github.com/realnedsanders/Coordination-Trilemma" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  main.pdf

# Check Rekor transparency log
# (URL provided in verification output)
```

## CI/CD Issues

### Workflows not triggering

**Cause:** Path filters or branch restrictions.

**Solution:**
- Check `.github/workflows/*.yml` path filters
- LaTeX builds trigger on changes to `src/tex/**`, `web/**`, `.github/workflows/latex-build-deploy.yml`
- Docker builds trigger on changes to `docker/**`, `.github/workflows/docker-build.yml`
- Changes to both trigger docker build first, then LaTeX build

### Build succeeds locally but fails in CI

**Cause:** Environment differences.

**Solution:**
```bash
# Check CI logs in GitHub Actions
# Common issues:
# 1. Path differences - CI uses /github/workspace
# 2. File permissions
# 3. Git configuration

# Test in clean environment
git clone https://github.com/realnedsanders/Coordination-Trilemma.git test-build
cd test-build
make
```

### Sign/deploy jobs skipped

**Cause:** Wrong event type or failed conditions.

**Solution:**
- Sign/deploy only run on push to main or after successful Docker rebuild
- Check workflow_run event succeeded
- Check event type matches conditions in yaml

## Performance Issues

### Builds very slow

**Possible causes:**
1. **First run:** Downloading Docker image (~500MB-1GB)
   - Subsequent builds much faster
   - `docker pull` progress shown

2. **Full TeXLive image:** Using ~4-5GB image
   - Solution: Use custom Alpine image (default)

3. **System resources:** Low memory or CPU
   - Docker container may be resource-constrained
   - Check Docker Desktop settings

4. **Disk I/O:** Slow disk or full filesystem
   - Check available space: `df -h`
   - Clean up: `docker system prune`

### Docker pull very slow

**Cause:** Network bandwidth or registry issues.

**Solution:**
```bash
# Check network
curl -I https://ghcr.io

# Try later if registry issues
# Or use cached image if available
docker images | grep coordination-trilemma
```

## Platform-Specific Issues

### macOS: "Docker Desktop is not running"

**Solution:**
- Open Docker Desktop application
- Wait for it to fully start (whale icon in menu bar)
- Try again

### Windows: WSL2 issues

**Solution:**
```powershell
# Ensure WSL2 is installed and updated
wsl --update

# Restart Docker Desktop
# Verify in PowerShell
docker ps
```

### Linux: SELinux denying access

**Solution:**
```bash
# Check SELinux status
getenforce

# Temporarily disable for testing
sudo setenforce 0

# Or configure SELinux policy
# (beyond scope - see SELinux docs)
```

## Still Having Issues?

### 1. Check Documentation
- [BUILD.md](BUILD.md) - Complete build documentation
- [docker-setup.md](docker-setup.md) - Docker-specific help
- [latex-guide.md](latex-guide.md) - LaTeX details
- [SECURITY.md](../.github/SECURITY.md) - Security verification

### 2. Check Existing Issues
- [GitHub Issues](https://github.com/realnedsanders/Coordination-Trilemma/issues)
- Search closed issues too

### 3. Gather Information
When reporting issues, include:
```bash
# System info
uname -a
docker --version
git --version

# Build output
make cleanall
make 2>&1 | tee build.log

# Attach build.log to issue
```

### 4. Open an Issue
- Use descriptive title
- Include steps to reproduce
- Attach logs and error messages
- Mention your platform (OS, Docker version)

---

**Quick Reference:**

| Problem | Quick Fix |
|---------|-----------|
| Docker not found | Install Docker, start daemon |
| Permission denied | Add user to docker group |
| PDF not generating | Check `src/tex/main.log` for errors |
| Slow build | First run downloads image |
| Git ownership error | `git config --global --add safe.directory "$(pwd)"` |
| Signature verification | Install cosign, check network |
| CI failure | Check GitHub Actions logs |

**Emergency Fallback:**
If Docker completely fails, you can build locally with LaTeX:
```bash
make local
# Requires local LaTeX installation
```
