# Makefile for Coordination Trilemma LaTeX document
# Uses Docker by default (no local LaTeX installation needed)

# Main tex file
MAIN = main
# Bibliography file
BIB = references

# Docker image for LaTeX compilation
# Can be overridden via environment variable (e.g., for CI to use custom image)
DOCKER_IMAGE ?= texlive/texlive:latest

# Docker command wrapper
# Runs container with current directory mounted, cleans up after
DOCKER_RUN = docker run --rm -v $(PWD):/workdir -w /workdir $(DOCKER_IMAGE)

# Local compilation commands (if you have LaTeX installed)
LATEX = pdflatex
BIBTEX = bibtex

# Choose compilation method: docker (default) or local
COMPILE_METHOD ?= docker

# Set commands based on compilation method
ifeq ($(COMPILE_METHOD),local)
    RUN_LATEX = $(LATEX)
    RUN_BIBTEX = $(BIBTEX)
else
    RUN_LATEX = $(DOCKER_RUN) $(LATEX)
    RUN_BIBTEX = $(DOCKER_RUN) $(BIBTEX)
endif

.PHONY: all quick clean cleanall view docker-pull docker-pull-custom help local

# Default target
all: $(MAIN).pdf

# Pull the Docker image (run this once to download)
docker-pull:
	@echo "Pulling LaTeX Docker image (this may take a few minutes)..."
	docker pull $(DOCKER_IMAGE)
	@echo "Docker image ready!"

# Pull the custom minimal image from GitHub Container Registry
docker-pull-custom:
	@echo "Pulling custom minimal LaTeX image from GitHub Container Registry..."
	@echo "Note: Replace 'realnedsanders' with your GitHub username if needed"
	docker pull ghcr.io/realnedsanders/coordination-trilemma/latex:latest
	@echo "Custom image ready! Use: DOCKER_IMAGE=ghcr.io/realnedsanders/coordination-trilemma/latex:latest make"

# Full build with bibliography
$(MAIN).pdf: $(MAIN).tex main-article.tex appendix-a.tex appendix-b.tex appendix-c.tex appendix-d.tex $(BIB).bib glossary.tex
	@echo "Compiling with $(COMPILE_METHOD) method..."
	$(RUN_LATEX) $(MAIN)
	$(RUN_BIBTEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	@echo "✓ PDF generated: $(MAIN).pdf"

# Quick build (no bibliography update)
quick:
	@echo "Quick compile with $(COMPILE_METHOD) method..."
	$(RUN_LATEX) $(MAIN)
	@echo "✓ Quick build complete"

# Use local LaTeX installation instead of Docker
local:
	@echo "Building with local LaTeX installation..."
	$(MAKE) all COMPILE_METHOD=local

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.synctex.gz

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf

# View the PDF (requires a PDF viewer)
view: $(MAIN).pdf
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(MAIN).pdf; \
	elif command -v open > /dev/null; then \
		open $(MAIN).pdf; \
	else \
		echo "No PDF viewer found. Please open $(MAIN).pdf manually."; \
	fi

# Interactive Docker shell (for debugging)
shell:
	docker run --rm -it -v $(PWD):/workdir -w /workdir $(DOCKER_IMAGE) /bin/bash

# Help message
help:
	@echo "Coordination Trilemma LaTeX Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make                   - Build PDF using Docker (default)"
	@echo "  make docker-pull       - Download LaTeX Docker image (run once)"
	@echo "  make docker-pull-custom - Download custom minimal image from ghcr.io"
	@echo "  make local             - Build using local LaTeX installation"
	@echo "  make quick             - Quick build without bibliography update"
	@echo "  make clean             - Remove auxiliary files"
	@echo "  make cleanall          - Remove all generated files including PDF"
	@echo "  make view              - Open the PDF"
	@echo "  make shell             - Open interactive Docker shell for debugging"
	@echo "  make help              - Show this help message"
	@echo ""
	@echo "First time setup:"
	@echo "  1. Install Docker: https://docs.docker.com/get-docker/"
	@echo "  2. Run: make docker-pull"
	@echo "  3. Run: make"
	@echo ""
	@echo "To use custom minimal image (smaller, faster):"
	@echo "  DOCKER_IMAGE=ghcr.io/realnedsanders/coordination-trilemma/latex:latest make"
	@echo ""
	@echo "To use local LaTeX instead of Docker:"
	@echo "  make local"
	@echo ""
	@echo "Current Docker image: $(DOCKER_IMAGE)"
	@echo "Current method: $(COMPILE_METHOD)"
