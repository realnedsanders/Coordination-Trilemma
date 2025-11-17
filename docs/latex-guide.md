# LaTeX Compilation Guide for Coordination Trilemma

**Last Updated:** 2025-11-17
**Audience:** Builders, Developers

This guide covers LaTeX compilation details for building the Coordination Trilemma paper.

## Project Structure

### LaTeX Source Files (`src/tex/`)

- `main.tex` - Main LaTeX document that includes all sections
- `main-article.tex` - The main article content
- `glossary.tex` - Glossary definitions
- `references.bib` - BibTeX bibliography file
- `appendices/` - Directory containing all appendices:
  - `appendix-a.tex` - Why No Alternative Path Exists
  - `appendix-b.tex` - Formal Mathematical Foundations
  - `appendix-c.tex` - Defense Mechanisms for Voluntary Coordination
  - `appendix-d.tex` - The Closing Window - Synthetic Media Evidence

### Build System

- `Makefile` - Build automation (at repository root)
- `scripts/generate-build-info.sh` - Build provenance generation
- `docker/Dockerfile.latex` - Custom Alpine-based LaTeX image

## Quick Start

### Prerequisites

**You only need Docker installed - no LaTeX installation required!**

1. Install Docker: <https://docs.docker.com/get-docker/>
2. That's it!

### First Time Setup

```bash
# Download our custom Alpine LaTeX image (only needed once, ~500MB-1GB)
make docker-pull

# Build your PDF
make
```

The PDF will be generated at `main.pdf` in the repository root.

### Common Commands

```bash
# Build PDF (uses Docker by default)
make

# View the generated PDF
make view

# Clean auxiliary files
make clean

# Clean everything including PDF
make cleanall

# Get help
make help

# Interactive Docker shell for debugging
make shell
```

**Note:** All builds automatically include bibliography processing. There's no separate "quick" build target.

### Alternative: Local LaTeX Installation

If you have LaTeX installed locally and prefer not to use Docker:

```bash
# Build using local installation
make local
```

### Manual Compilation (Without Make)

If you prefer to run Docker commands directly:

```bash
# Pull our custom image first
docker pull ghcr.io/realnedsanders/coordination-trilemma/latex:latest

# Compile (run from project root directory)
docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir/src/tex \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest \
  pdflatex main

docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir/src/tex \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest \
  bibtex main

# Run pdflatex twice more for cross-references
docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir/src/tex \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest \
  pdflatex main

docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir/src/tex \
  ghcr.io/realnedsanders/coordination-trilemma/latex:latest \
  pdflatex main
```

The PDF will be generated in `src/tex/` and needs to be moved to root manually.

## Document Structure

The document uses the `amsart` class (American Mathematical Society article style), which is ideal
for mathematics-heavy content.

### Main Structure

```text
src/tex/main.tex
├── Preamble (packages, theorem environments, metadata)
├── Abstract
├── Table of Contents
├── main-article.tex (Sections 1-9)
├── appendices/
│   ├── appendix-a.tex
│   ├── appendix-b.tex
│   ├── appendix-c.tex
│   └── appendix-d.tex
└── Bibliography (from references.bib)
```

## Customization

### Author Information

Edit the following lines in `src/tex/main.tex`:

```latex
\author{Your Name}
\address{Your Institution}
\email{your.email@example.com}
```

### Title or Abstract

Modify directly in `src/tex/main.tex`.

### Adding Citations

1. Add entries to `src/tex/references.bib` in BibTeX format
2. Cite in text using `\cite{key}`
3. Recompile (bibliography processing is automatic with `make`)

Example:

```latex
As shown by \cite{kahneman1979prospect}, ...
```

## Requirements

### Docker Method (Recommended)

- **Docker** - That's it! Everything else is in the container
- Our custom Alpine-based image includes minimal TeX Live with required packages only (~500MB-1GB)
- Much smaller and faster than full TeX Live (~4-5GB)

### Local Method (Alternative)

If you choose to compile locally (`make local`):

- Complete TeX distribution (TeX Live 2022+ or MiKTeX)
- Required packages (usually included):
  - amsmath, amssymb, amsthm (mathematical typesetting)
  - hyperref (clickable links and PDF metadata)
  - booktabs (professional tables)
  - graphicx (if you add figures)

## Troubleshooting

### Docker Issues

**Need additional LaTeX packages:**

- Our custom image is optimized (~500MB-1GB) and includes packages needed for this document
- If you add packages not in the custom image, use the full TeXLive image:

  ```bash
  DOCKER_IMAGE=texlive/texlive:latest make
  ```

- The full image is ~4-5GB but includes all TeX packages

**Permission errors on generated files:**

- Docker runs as root, files may be owned by root
- Fix: `sudo chown -R $USER:$USER .`
- Or add this to Makefile: `--user $(id -u):$(id -g)`

**Docker not found:**

- Install Docker: <https://docs.docker.com/get-docker/>
- Make sure Docker daemon is running

**Slow compilation:**

- First run downloads the image (one-time, ~500MB-1GB download)
- Subsequent builds are much faster (no download needed)
- Compilation itself takes ~30-60 seconds depending on your system

### LaTeX Issues

**Bibliography not appearing:**

- The full `make` automatically processes the bibliography
- Check that `src/tex/references.bib` exists and has valid BibTeX entries

**Citations showing as [?]:**

- Run the full compilation: `make clean && make`

**Cross-references not working:**

- The Makefile runs pdflatex 3 times automatically
- If still broken: `make clean && make`

### Manual Fixes

If automatic conversion missed something:

1. The appendix .tex files can be edited directly
2. Mathematical notation is preserved as-is from Markdown
3. Tables may need manual adjustment for complex formatting

## Notes on Conversion

### What Was Preserved

- All mathematical notation (already in LaTeX format)
- Section structure and hierarchy
- Lists (itemize and enumerate)
- Tables (converted to tabular environment)
- Emphasis and bold text

### What May Need Manual Review

- Complex Markdown tables (check formatting)
- Special characters in non-math mode
- Links (converted to \url{})
- Any custom Markdown extensions

### Checking the Conversion

Review each appendix .tex file, particularly:

- Table formatting (Appendix D has several tables)
- Mathematical theorem environments (Appendix B)
- List structures (all appendices)

## Submission to SocArXiv

For SocArXiv submission:

1. Compile the PDF using `make` or manual compilation
2. Submit `main.pdf` as your manuscript
3. Optionally, include all .tex files as supplementary materials
4. The PDF includes proper metadata (set in main.tex hyperref config)

## Further Customization

### Changing Document Class

To use a different class (e.g., standard `article`):

```latex
\documentclass[12pt]{article}
```

Note: You may need to adjust theorem environments for non-AMS classes.

### Adding Figures

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.8\textwidth]{filename.pdf}
  \caption{Your caption}
  \label{fig:label}
\end{figure}
```

## License and Attribution

Follow the same license as the original Markdown files.

## Questions or Issues

If you encounter problems with the LaTeX conversion:

1. Check the compilation log (.log file) for specific errors
2. Review the section causing issues in the .tex file
3. Most Markdown elements should convert cleanly to LaTeX

## Why Docker + pdflatex?

### Why Docker?

- **No installation hassle** - No need to install multi-GB TeX distributions
- **Reproducible** - Same environment on any machine
- **Isolated** - Won't conflict with other software
- **Cross-platform** - Works on Linux, Mac, Windows (via Docker Desktop)

### Why pdflatex (not pandoc)?

- **Better math support** - Professional mathematical typesetting
- **Custom formatting** - Full control with amsart class
- **Bibliography** - Seamless BibTeX integration  
- **Theorem environments** - Numbered theorems, definitions, lemmas
- **Academic standard** - What journals and arXiv expect

Pandoc is great for quick conversions, but for a formal mathematics paper going to SocArXiv, pdflatex produces superior results.

## Docker Image Details

**Default Image:** `ghcr.io/realnedsanders/coordination-trilemma/latex:latest`

This custom Alpine-based image provides:

- Minimal TeX Live distribution with required packages only
- **Size:** ~500MB-1GB (much smaller than full TeX Live)
- **Base:** Alpine Linux edge
- **Packages:** TeXLive, TeXLive-latexextra, TeXLive-bibtexextra, TeXLive-latexrecommended, TeXLive-pictures
- **Tools:** pdflatex, bibtex, ChkTeX (linting), make, git, perl
- **Updates:** Automatically rebuilt and signed when Dockerfile changes
- **Security:** Cryptographically signed with Cosign, includes SLSA provenance

### Alternative Images

To use the full TeXLive image (~4-5GB with all packages):

```bash
DOCKER_IMAGE=texlive/texlive:latest make
```

The custom image is defined in `docker/Dockerfile.latex` and optimized for this specific document.

## Advanced Usage

### Interactive Debugging

Drop into a shell inside the Docker container:

```bash
make shell

# Now you're inside the container at /workdir (your project directory)
# Try commands like:
pdflatex main
ls -la
cat main.log
```

### Building in CI/CD

This project uses GitHub Actions with our custom Docker image. The Makefile automatically detects
CI environments and uses local compilation (since it's already inside a container).

See [CI/CD.md](CI/CD.md) for complete workflow documentation.

**Key points:**

- CI runs inside the `ghcr.io/realnedsanders/coordination-trilemma/latex:latest` container
- Makefile sets `COMPILE_METHOD=local` when `GITHUB_ACTIONS` env var is set
- Git provenance is automatically embedded in the PDF
- PDF is cryptographically signed before deployment

### Custom Docker Image

Our custom image is defined in `docker/Dockerfile.latex`. To modify it:

1. Edit `docker/Dockerfile.latex`
2. Push changes to trigger automatic rebuild
3. GitHub Actions will build, sign, and publish the new image
4. Subsequent builds will use the updated image

To add TeXLive packages:

```dockerfile
# In docker/Dockerfile.latex
RUN apk add --no-cache \
    texlive \
    texlive-yourpackage
```

**Note:** Changes to Dockerfiles trigger a full rebuild cycle before document builds run.
