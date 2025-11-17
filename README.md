# Coordination Trilemma

A formal analysis of coordination mechanisms at civilization scale, examining the structural constraints that limit viable approaches to large-scale human cooperation.

## 🔐 Security & Provenance

This project achieves **SLSA Build Level 3** with cryptographically signed artifacts:
- ✅ **Docker images** signed with Cosign (keyless)
- ✅ **PDF artifacts** signed with Cosign
- ✅ **SLSA provenance** attestations
- ✅ **SBOM** (Software Bill of Materials)
- ✅ **Build metadata** embedded in artifacts

**Verify artifacts:**
```bash
./scripts/verify-signatures.sh
```

See **[docs/SECURITY.md](docs/SECURITY.md)** for complete security documentation.

## 🚀 Quick Start

### Build the PDF

```bash
# Using Docker (recommended)
make docker-pull
make

# Or using local LaTeX
make local
```

### View the PDF

```bash
make view
```

### Clean up

```bash
make clean      # Remove build artifacts
make cleanall   # Remove everything including PDF
```

## 📚 Documentation

All documentation is in the [`docs/`](docs/) directory:

- **[Quick Start Guide](docs/quickstart.md)** - Get started quickly
- **[README](docs/README.md)** - Detailed project information
- **[LaTeX Guide](docs/latex-guide.md)** - LaTeX compilation details
- **[Docker Setup](docs/docker-setup.md)** - Docker-specific instructions
- **[Security](docs/SECURITY.md)** - Security and provenance verification
- **[SLSA Roadmap](docs/SLSA_ROADMAP.md)** - Path to SLSA Level 4

## 📁 Project Structure

```
.
├── src/
│   ├── tex/              # LaTeX source files
│   │   ├── appendices/   # Document appendices
│   │   ├── main.tex      # Main document
│   │   └── ...
│   └── md/               # Markdown versions
├── docs/                 # All documentation
├── scripts/              # Build and verification scripts
├── web/                  # GitHub Pages content
├── build/                # Build outputs (gitignored)
├── Makefile             # Build automation
├── Dockerfile           # Custom Alpine LaTeX image
└── Dockerfile.security-tools  # Custom security tools image
```

## 🔄 CI/CD Infrastructure

All CI workflows use custom Alpine-based Docker images for faster, more reproducible builds:

- **`latex:latest`** - Minimal Alpine image with TeXLive and ChkTeX for document compilation and linting
- **`security-tools:latest`** - Minimal Alpine image with Cosign for artifact signing

These images are automatically built and signed on every change to Dockerfiles. No tools are installed during CI runs, ensuring consistent environments and faster execution.

## 🔧 Development

```bash
# Build with custom Docker image
make

# Quick build (no bibliography update)
make quick

# Interactive Docker shell
make shell

# Help
make help
```

## 📄 License

See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [docs/README.md](docs/README.md) for contribution guidelines and project details.

## 📖 Published Version

The latest build is automatically published to GitHub Pages:
- **Landing page**: https://realnedsanders.github.io/Coordination-Trilemma/
- **Direct PDF**: https://realnedsanders.github.io/Coordination-Trilemma/main.pdf
