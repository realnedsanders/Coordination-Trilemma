# Quick Start Guide

**Last Updated:** 2025-11-17
**Audience:** New Users

Get the Coordination Trilemma PDF built in 2 steps.

## 🚀 Get Your PDF in 2 Steps

### Step 1: Install Docker

```bash
# macOS
brew install --cask docker

# Windows
# Download from: https://docs.docker.com/desktop/install/windows-install/

# Linux (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Step 2: Build Your Paper

```bash
# Download our custom LaTeX image (only needed once, ~500MB-1GB)
make docker-pull

# Generate PDF
make

# Done! Your PDF is ready at: main.pdf
```

The PDF is generated at the repository root as `main.pdf`.

## 📖 Common Commands

```bash
make              # Build complete PDF with bibliography
make quick        # Fast build (skip bibliography)
make view         # Open the PDF
make clean        # Remove temporary files
make help         # Show all available commands
```

## 🎯 What You Get

- **main.pdf** - Complete paper with all sections and appendices (at repository root)
- Professional mathematical typesetting (amsart class)
- Proper bibliography with BibTeX
- Numbered theorems and cross-references
- Embedded build provenance (git commit, date, platform)
- Cryptographically signed (when built in CI)

## 🔧 Customization

### Add Your Name

Edit `src/tex/main.tex` (author section):

```latex
\author{Your Name Here}
\address{Your Institution}
\email{your.email@example.com}
```

### Edit Content

- Main article: `src/tex/main-article.tex`
- Appendices: `src/tex/appendices/appendix-a.tex` through `appendix-d.tex`
- Bibliography: `src/tex/references.bib`

### Rebuild After Changes

```bash
make
```

## ❓ Troubleshooting

**PDF not generating?**

```bash
# Check Docker is running
docker ps

# Clean and rebuild
make cleanall
make
```

**Permission errors?**

```bash
# Fix file ownership (Linux/Mac)
sudo chown -R $USER:$USER .
```

**Want more details?**

- See [BUILD.md](BUILD.md) for comprehensive documentation
- Run `make help` for all available commands

## 🎓 Why This Setup?

✅ **No LaTeX installation needed** - Everything runs in Docker
✅ **Works everywhere** - Same result on Mac, Windows, Linux
✅ **Professional output** - amsart class for academic mathematics
✅ **Reproducible** - Share the .tex files, anyone can build the PDF

## Next Steps

1. Customize author information in `src/tex/main.tex`
2. Run `make` to generate your PDF
3. Review the output at `main.pdf` (repository root)
4. Verify signatures: `./scripts/verify-signatures.sh`
5. Share your research at enlightenment.dev!

For detailed documentation, see [BUILD.md](BUILD.md).
