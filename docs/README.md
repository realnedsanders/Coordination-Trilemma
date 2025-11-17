# Coordination Trilemma - Documentation

This directory contains all technical and development documentation for the Coordination Trilemma project.

## Documentation Index

### For Readers
- **[Main README](../README.md)** - Overview of the paper's content and arguments

### For Builders
- **[BUILD.md](BUILD.md)** - Complete build instructions and project structure
- **[Quick Start Guide](quickstart.md)** - Get started quickly with building the PDF
- **[LaTeX Guide](latex-guide.md)** - LaTeX compilation details and troubleshooting
- **[Docker Setup](docker-setup.md)** - Docker-specific instructions

### For Security & Verification
- **[SECURITY.md](SECURITY.md)** - Security documentation and artifact verification
- **[SLSA Roadmap](SLSA_ROADMAP.md)** - Path to SLSA Build Level 4

## Quick Links

**Building the PDF:**
```bash
make docker-pull
make
```

**Verifying Signatures:**
```bash
./scripts/verify-signatures.sh
```

**Published Version:**
- Landing page: https://enlightenment.dev
- Direct PDF: https://enlightenment.dev/main.pdf

## Contributing

This is an academic paper under active development. We welcome:
- Corrections to mathematical proofs or logical errors
- Additional historical evidence or counterexamples
- Clarifications of ambiguous statements
- References to relevant literature

Please open an issue or submit a pull request. Changes to the main argument require substantial justification.

See [BUILD.md](BUILD.md) for information about the project structure and development workflow.
