# LaTeX Compilation Guide for Coordination Trilemma

## Files Created

### Main Files
- `main.tex` - Main LaTeX document that includes all sections
- `main-article.tex` - The main article content (converted from README.md)
- `references.bib` - BibTeX bibliography file

### Appendices
- `appendix-a.tex` - Appendix A: Why No Alternative Path Exists
- `appendix-b.tex` - Appendix B: Formal Mathematical Foundations
- `appendix-c.tex` - Appendix C: Defense Mechanisms for Voluntary Coordination
- `appendix-d.tex` - Appendix D: The Closing Window - Synthetic Media Evidence

### Utilities
- `Makefile` - Build automation
- `md_to_latex.py` - Markdown to LaTeX conversion script

## Quick Start

### Prerequisites

**You only need Docker installed - no LaTeX installation required!**

1. Install Docker: https://docs.docker.com/get-docker/
2. That's it!

### First Time Setup

```bash
# Download the LaTeX Docker image (only needed once, ~2GB)
make docker-pull

# Build your PDF
make
```

### Common Commands

```bash
# Build PDF (uses Docker by default)
make

# Quick build (no bibliography update)
make quick

# View the generated PDF
make view

# Clean auxiliary files
make clean

# Clean everything including PDF
make cleanall

# Get help
make help
```

### Alternative: Local LaTeX Installation

If you have LaTeX installed locally and prefer not to use Docker:

```bash
# Build using local installation
make local
```

### Manual Compilation (Without Make)

If you prefer to run Docker commands directly:

```bash
# Pull the image first
docker pull texlive/texlive:latest

# Compile (run from project directory)
docker run --rm -v $(pwd):/workdir -w /workdir texlive/texlive:latest pdflatex main
docker run --rm -v $(pwd):/workdir -w /workdir texlive/texlive:latest bibtex main
docker run --rm -v $(pwd):/workdir -w /workdir texlive/texlive:latest pdflatex main
docker run --rm -v $(pwd):/workdir -w /workdir texlive/texlive:latest pdflatex main
```

## Document Structure

The document uses the `amsart` class (American Mathematical Society article style), which is ideal for mathematics-heavy content.

### Main Structure
```
main.tex
├── Preamble (packages, theorem environments, metadata)
├── Abstract
├── Table of Contents
├── main-article.tex (Sections 1-9)
├── appendix-a.tex
├── appendix-b.tex
├── appendix-c.tex
├── appendix-d.tex
└── Bibliography (from references.bib)
```

## Customization

### Author Information
Edit the following lines in `main.tex`:
```latex
\author{Your Name}
\address{Your Institution}
\email{your.email@example.com}
```

### Title or Abstract
Modify directly in `main.tex`.

### Adding Citations
1. Add entries to `references.bib` in BibTeX format
2. Cite in text using `\cite{key}`
3. Recompile with bibliography processing

Example:
```latex
As shown by \cite{kahneman1979prospect}, ...
```

## Requirements

### Docker Method (Recommended)
- **Docker** - That's it! Everything else is in the container
- The Docker image includes a complete TeX Live distribution with all packages

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

**Docker image too large:**
- The texlive/texlive image is ~2GB (contains full TeX Live)
- Alternative: Use `texlive/texlive:latest-small` (edit Makefile line 10)
- Smaller image may be missing some packages

**Permission errors on generated files:**
- Docker runs as root, files may be owned by root
- Fix: `sudo chown -R $USER:$USER .`
- Or add this to Makefile: `--user $(id -u):$(id -g)`

**Docker not found:**
- Install Docker: https://docs.docker.com/get-docker/
- Make sure Docker daemon is running

**Slow compilation:**
- First run downloads the image (one-time ~5 min)
- Subsequent builds are fast
- Use `make quick` for faster incremental builds

### LaTeX Issues

**Bibliography not appearing:**
- Make sure you run the full `make` (not `make quick`)
- Check that `references.bib` is in the same directory

**Citations showing as [?]:**
- Run the full compilation: `make clean && make`

**Cross-references not working:**
- The Makefile runs pdflatex 3 times automatically
- If still broken: `make clean && make`

### Manual Fixes

If automatic conversion missed something:
1. The appendix .tex files can be edited directly
2. Mathematical notation is preserved as-is from markdown
3. Tables may need manual adjustment for complex formatting

## Notes on Conversion

### What Was Preserved
- All mathematical notation (already in LaTeX format)
- Section structure and hierarchy
- Lists (itemize and enumerate)
- Tables (converted to tabular environment)
- Emphasis and bold text

### What May Need Manual Review
- Complex markdown tables (check formatting)
- Special characters in non-math mode
- Links (converted to \url{})
- Any custom markdown extensions

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

Follow the same license as the original markdown files.

## Questions or Issues

If you encounter problems with the LaTeX conversion:
1. Check the compilation log (.log file) for specific errors
2. Review the section causing issues in the .tex file
3. Most markdown elements should convert cleanly to LaTeX

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

The Makefile uses `texlive/texlive:latest` which provides:
- Complete TeX Live distribution
- All common LaTeX packages pre-installed
- pdflatex, bibtex, and related tools
- Regular updates from the TeX Live team

### Alternative Images

Edit line 10 of the Makefile to use a different image:

```makefile
# Smaller image (~400MB vs 2GB)
DOCKER_IMAGE = texlive/texlive:latest-small

# Or use a specific year
DOCKER_IMAGE = texlive/texlive:TL2023-historic
```

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

The Docker approach works great in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Build PDF
  run: |
    docker pull texlive/texlive:latest
    make
    
- name: Upload PDF
  uses: actions/upload-artifact@v3
  with:
    name: paper
    path: main.pdf
```

### Custom Docker Image

If you need additional packages, create a custom Dockerfile:

```dockerfile
FROM texlive/texlive:latest
RUN tlmgr install <package-name>
```

Then update the Makefile to use your custom image.
