# Contributing to the Coordination Trilemma

**Last Updated:** 2025-11-17

Thank you for your interest in contributing to the Coordination Trilemma project! This document
provides guidelines for contributing to this academic paper and its build infrastructure.

## Types of Contributions

We welcome several types of contributions:

### 1. Content Contributions

- **Corrections to mathematical proofs or logical errors**
- **Additional historical evidence or counterexamples**
- **Clarifications of ambiguous statements**
- **References to relevant literature**

**Important:** Changes to the main argument require substantial justification. This is an
academic paper with specific claims, not a wiki.

### 2. Documentation Improvements

- Fix typos or unclear instructions
- Add examples or clarifications
- Improve navigation between docs
- Update outdated information

### 3. Build System Improvements

- Docker image optimizations
- Build script enhancements
- CI/CD workflow improvements
- Security enhancements

### 4. Security Reports

- See [SECURITY.md](SECURITY.md) for reporting security issues

## How to Contribute

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/Coordination-Trilemma.git
cd Coordination-Trilemma
```

### 2. Create a Branch

```bash
git checkout -b your-feature-name
```

Use descriptive branch names:

- `fix/typo-in-appendix-b`
- `feat/add-reproducibility-test`
- `docs/clarify-build-process`

### 3. Make Your Changes

#### For LaTeX Content

- Edit files in `src/tex/`
- Test your build: `make clean && make`
- Ensure the PDF compiles without errors
- Verify mathematical notation renders correctly

#### For Documentation

- Edit files in `docs/` or root README
- Update "Last Updated" dates
- Check all links work
- Follow existing formatting style

#### For Build System

- Test changes locally before submitting
- Document any new environment variables or flags
- Update relevant documentation

### 4. Test Your Changes

**Minimum testing required:**

```bash
# Clean build test
make cleanall
make

# Verify PDF generates correctly
ls -lh main.pdf

# Check for LaTeX warnings
cat src/tex/*.log | grep -i warning
```

**For build system changes:**

- Test both Docker and local builds
- Verify CI workflows would pass (if possible)
- Test on a clean clone if making structural changes

### 5. Commit Your Changes

Follow conventional commits format:

```bash
git commit -m "fix: correct typo in Appendix B proof"
git commit -m "docs: clarify Docker setup for Windows"
git commit -m "feat: add reproducibility test workflow"
```

**Commit message types:**

- `fix:` - Bug fixes
- `feat:` - New features
- `docs:` - Documentation changes
- `style:` - Formatting, no code change
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Description

Use the PR template (automatically provided). Include:

- Clear description of changes
- Type of change (bug fix, feature, docs, etc.)
- Testing performed
- Security checklist (if applicable)

### PR Title

Use the same conventional commit format:

- `fix: correct typo in section 3`
- `docs: update Docker setup guide`
- `feat: add SLSA Level 4 reproducibility`

### Review Process

1. **Automated checks** run (linting, build, security scan)
2. **Maintainer review** - at least one approval required
3. **Discussion** - respond to feedback promptly
4. **Approval** - maintainer approves when ready
5. **Merge** - maintainer merges (or you can merge if approved)

**Note:** This project aims for SLSA Level 4, which requires two-person review. All changes must
be reviewed by a code owner before merging.

## Code Style Guidelines

### LaTeX

- Use `amsart` document class conventions
- Keep lines under 100 characters where practical
- Use `\cite{}` for citations
- Use theorem environments consistently
- Comment complex mathematical derivations

### Markdown (Documentation)

- Use ATX-style headers (`#` not underlines)
- Code blocks with language specification
- Keep lines under 100 characters
- Use relative links for internal docs
- Include "Last Updated" dates

### Shell Scripts

- Use `#!/bin/bash` or `#!/bin/sh` as appropriate
- Include header comments explaining purpose
- Use `set -e` to fail on errors
- Quote variables: `"$VAR"` not `$VAR`
- Document all functions

### Makefile

- Use tabs not spaces for indentation
- Document targets with comments
- Keep target names lowercase
- Use `.PHONY` for non-file targets

## Documentation Requirements

When making changes, update relevant documentation:

**Content changes** → Update paper itself + README summary

**Build system changes** → Update BUILD.md, Makefile comments

**Docker changes** → Update Docker-setup.md, Dockerfile comments

**Security changes** → Update SECURITY.md, verification scripts

**Workflow changes** → Create/update CI/CD.md

## Testing Requirements

### Minimum Tests (Required)

- [ ] Clean build succeeds (`make cleanall && make`)
- [ ] PDF generates without errors
- [ ] No new LaTeX warnings introduced
- [ ] Documentation builds/renders correctly

### Recommended Tests

- [ ] Build with Docker
- [ ] Build with local LaTeX (if available)
- [ ] Test on clean repository clone
- [ ] Verify links in documentation

### For Build System Changes

- [ ] Test both `COMPILE_METHOD=docker` and `COMPILE_METHOD=local`
- [ ] Verify environment variable handling
- [ ] Check error handling for missing dependencies
- [ ] Test on multiple platforms (Linux/macOS/Windows if possible)

## Security Guidelines

### Sensitive Information

- **Never commit** secrets, API keys, or credentials
- **Never commit** private/draft content not meant for publication
- Use `.gitignore` for sensitive files
- Review diffs before committing

### Dependencies

- Pin versions when adding dependencies
- Document why new dependencies are needed
- Prefer smaller, well-maintained packages
- Check for known vulnerabilities

### Docker Images

- Minimize image size
- Use official base images or well-maintained alternatives
- Document all installed packages
- Sign images with Cosign (done automatically in CI)

## Getting Help

**Questions about:**

- **Content/Paper:** Open an issue with `[question]` tag
- **Build System:** See [BUILD.md](docs/BUILD.md) or [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Security:** See [SECURITY.md](SECURITY.md)
- **Contributing Process:** Open an issue with `[meta]` tag

**Before opening an issue:**

1. Check existing issues (open and closed)
2. Review documentation in `docs/`
3. Try troubleshooting steps in TROUBLESHOOTING.md

## Code of Conduct

### Be Respectful

- Assume good faith
- Be patient with newcomers
- Critique ideas, not people
- Accept constructive criticism gracefully

### Be Constructive

- Provide specific, actionable feedback
- Explain *why* something should change
- Offer alternatives when rejecting ideas
- Help improve contributions rather than just rejecting them

### Be Professional

- Keep discussions on-topic
- Avoid inflammatory language
- Respect intellectual disagreement
- Remember this is an academic project

## License & Copyright

This project uses **dual licensing**. By contributing, you agree that:

### Academic Content Contributions

Contributions to the paper (LaTeX source, article text, proofs, arguments) will be licensed
under **Creative Commons Attribution 4.0 International (CC-BY 4.0)**.

**You agree:**

- Your contribution is your original work or properly attributed
- It will be licensed under CC-BY 4.0
- Others may use, share, and adapt it with attribution
- You retain copyright but grant broad usage rights

### Software/Infrastructure Contributions

Contributions to build system, scripts, Docker files, workflows, and documentation will be
licensed under **GNU Affero General Public License v3.0 (AGPLv3)**.

**You agree:**

- Your contribution is your original work
- It will be licensed under AGPLv3
- Derivative works must also be AGPLv3
- Network use triggers distribution requirements

### Which Applies to My Contribution?

- Editing `.tex` files in `src/tex/`? → **CC-BY 4.0**
- Editing Makefile, scripts, Docker files? → **AGPLv3**
- Editing documentation? → **AGPLv3**
- When in doubt, ask in your PR

See [LICENSE](LICENSE) for complete details on the dual licensing structure and rationale.

## Recognition

Contributors who make significant contributions will be acknowledged in the paper's
acknowledgments section (at maintainer discretion).

## Questions?

Open an issue with `[question]` tag or reach out to maintainers directly through GitHub.

---

**Thank you for contributing to the Coordination Trilemma project!**
