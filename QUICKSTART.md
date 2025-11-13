# Quick Start Guide

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
# Download LaTeX image (only needed once, ~2GB)
make docker-pull

# Generate PDF
make

# Done! Your PDF is ready: main.pdf
```

## 📖 Common Commands

```bash
make              # Build complete PDF with bibliography
make quick        # Fast build (skip bibliography)
make view         # Open the PDF
make clean        # Remove temporary files
make help         # Show all available commands
```

## 🎯 What You Get

- **main.pdf** - Your complete paper with all sections and appendices
- Professional mathematical typesetting (amsart class)
- Proper bibliography with BibTeX
- Numbered theorems and cross-references
- Ready for SocArXiv submission

## 🔧 Customization

### Add Your Name
Edit `main.tex` lines 33-35:
```latex
\author{Your Name Here}
\address{Your Institution}
\email{your.email@example.com}
```

### Edit Content
- Main article: `main-article.tex`
- Appendices: `appendix-a.tex` through `appendix-d.tex`
- Bibliography: `references.bib`

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
- See `LATEX_README.md` for comprehensive documentation
- Run `make help` for all available commands

## 🎓 Why This Setup?

✅ **No LaTeX installation needed** - Everything runs in Docker
✅ **Works everywhere** - Same result on Mac, Windows, Linux
✅ **Professional output** - amsart class for academic mathematics
✅ **Reproducible** - Share the .tex files, anyone can build the PDF

## Next Steps

1. Customize author information in `main.tex`
2. Run `make` to generate your PDF
3. Review the output in `main.pdf`
4. Submit to SocArXiv!

For detailed documentation, see `LATEX_README.md`.
