# Build Documentation

This document contains technical information for building and developing the Coordination Trilemma LaTeX document.

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

## Docker Images

This project uses a custom minimal Alpine-based LaTeX image by default for fast, lightweight builds.

### Custom Alpine Image (Default)
- **Size**: ~500MB-1GB (much smaller than full TeXLive!)
- **Pros**: Alpine edge-based, faster downloads, secure, includes only packages needed for this document
- **Location**: `ghcr.io/realnedsanders/coordination-trilemma/latex:latest`
- **Auto-built**: CI automatically rebuilds when `Dockerfile` changes
- **Usage**: Default when running `make`

### Full TeXLive Image (Alternative)
- **Size**: ~4-5GB
- **Pros**: Includes all LaTeX packages
- **When to use**: If you add packages not included in the custom image

To use the full TeXLive image:

```bash
DOCKER_IMAGE=texlive/texlive:latest make
```

## 🔄 CI/CD Infrastructure

All CI workflows use custom Alpine-based Docker images for faster, more reproducible builds:

- **`latex:latest`** - Minimal Alpine image with TeXLive and ChkTeX for document compilation and linting
- **`security-tools:latest`** - Minimal Alpine image with Cosign for artifact signing

These images are automatically built and signed on every change to Dockerfiles. No tools are installed during CI runs, ensuring consistent environments and faster execution.

### Continuous Integration

This repository uses GitHub Actions to automatically:
- **Build custom Docker image**: Rebuilds minimal Alpine-based image when Dockerfile changes
- **Lint LaTeX files**: Checks all .tex files using ChkTeX
- **Build the PDF**: Compiles using the custom minimal image
- **Sign the PDF**: Cryptographically signs PDF with Cosign (keyless) and generates SLSA provenance
- **Deploy to GitHub Pages**: Publishes the **signed** PDF to https://enlightenment.dev

The workflow ensures that only cryptographically signed PDFs are deployed to production. The signature bundle (`main.pdf.cosign.bundle`) is also deployed and can be used to verify authenticity.

## 📁 Project Structure

```
.
├── src/
│   ├── tex/              # LaTeX source files
│   │   ├── appendices/   # Document appendices
│   │   ├── main.tex      # Main document
│   │   ├── main-article.tex  # Article content
│   │   ├── glossary.tex  # Glossary definitions
│   │   └── references.bib    # Bibliography
│   └── md/               # Markdown versions
├── docs/                 # All documentation
│   ├── BUILD.md          # This file
│   ├── SECURITY.md       # Security and provenance
│   ├── quickstart.md     # Quick start guide
│   ├── latex-guide.md    # LaTeX compilation details
│   └── docker-setup.md   # Docker-specific instructions
├── scripts/              # Build and verification scripts
│   ├── generate-build-info.sh  # Build provenance script
│   └── verify-signatures.sh    # Security verification script
├── web/                  # GitHub Pages content
├── build/                # Build outputs (gitignored)
├── Makefile             # Build automation
├── Dockerfile           # Custom Alpine LaTeX image
└── Dockerfile.security-tools  # Custom security tools image
```

## Requirements

- Docker (for containerized builds)
- OR a local LaTeX installation with pdflatex and bibtex

## GitHub Pages Setup

The CI automatically deploys the latest PDF to GitHub Pages. To enable this:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Build and deployment**:
   - **Source**: Select "GitHub Actions"
4. Save the settings

After the next push to `main`, your PDF will be available at:
- **Landing page**: https://enlightenment.dev
- **Direct PDF link**: https://enlightenment.dev/main.pdf

### Customizing the Landing Page

The landing page is defined in `web/index.html`. You can edit this file to customize the appearance, add additional content, or change the styling.

## Contributing

Changes pushed to `main` will automatically trigger a new build and update the published PDF.

See the [main README](../README.md) for contribution guidelines and project details.
