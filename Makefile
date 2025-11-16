# Makefile for Coordination Trilemma LaTeX document
# Uses Docker by default (no local LaTeX installation needed)

# Source directories
SRC_DIR = src/tex
SCRIPTS_DIR = scripts
BUILD_DIR = build

# Main tex file (in src/tex/)
MAIN = main
# Bibliography file
BIB = references

# Docker image for LaTeX compilation
# Can be overridden via environment variable
# Using custom Alpine-based image by default (much smaller and faster)
DOCKER_IMAGE ?= ghcr.io/realnedsanders/coordination-trilemma/latex:latest

# Docker command wrapper
# Runs container with current directory mounted, cleans up after
# Working directory set to src/tex for LaTeX compilation
# Note: Runs as root in container, but files are accessible due to volume mount
DOCKER_RUN = docker run --rm -v $(PWD):/workdir -w /workdir/$(SRC_DIR) $(DOCKER_IMAGE)

# Local compilation commands (if you have LaTeX installed)
LATEX = pdflatex
BIBTEX = bibtex

# Choose compilation method: docker (default) or local
COMPILE_METHOD ?= docker

# Set commands based on compilation method
ifeq ($(COMPILE_METHOD),local)
    RUN_LATEX = cd $(SRC_DIR) && $(LATEX)
    RUN_BIBTEX = cd $(SRC_DIR) && $(BIBTEX)
else
    RUN_LATEX = $(DOCKER_RUN) $(LATEX)
    RUN_BIBTEX = $(DOCKER_RUN) $(BIBTEX)
endif

.PHONY: all quick clean cleanall view docker-pull docker-pull-full help local

# Ensure build directory exists
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

# Default target
all: $(BUILD_DIR) $(MAIN).pdf

# Pull the Docker image (run this once to download)
docker-pull:
	@echo "Pulling custom Alpine-based LaTeX image..."
	docker pull $(DOCKER_IMAGE)
	@echo "Docker image ready!"

# Pull the full TeXLive image (larger, includes all packages)
docker-pull-full:
	@echo "Pulling full TeXLive Docker image (this may take a few minutes, ~4-5GB)..."
	docker pull texlive/texlive:latest
	@echo "Full TeXLive image ready! Use: DOCKER_IMAGE=texlive/texlive:latest make"

# Generate build information from git metadata
$(BUILD_DIR)/build-info.tex: | $(BUILD_DIR)
	@echo "Generating build information..."
	@$(SCRIPTS_DIR)/generate-build-info.sh
	@mv build-info.tex $(BUILD_DIR)/ 2>/dev/null || true

# Full build with bibliography
$(MAIN).pdf: $(BUILD_DIR)/build-info.tex $(SRC_DIR)/$(MAIN).tex $(SRC_DIR)/main-article.tex $(SRC_DIR)/appendices/*.tex $(SRC_DIR)/$(BIB).bib $(SRC_DIR)/glossary.tex
	@echo "Compiling with $(COMPILE_METHOD) method..."
	@cp $(BUILD_DIR)/build-info.tex $(SRC_DIR)/ || true
	$(RUN_LATEX) $(MAIN)
	$(RUN_BIBTEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	@cp $(SRC_DIR)/$(MAIN).pdf . || true
	@echo "✓ PDF generated: $(MAIN).pdf"

# Quick build (no bibliography update)
quick: $(BUILD_DIR)/build-info.tex
	@echo "Quick compile with $(COMPILE_METHOD) method..."
	@cp $(BUILD_DIR)/build-info.tex $(SRC_DIR)/ || true
	$(RUN_LATEX) $(MAIN)
	@cp $(SRC_DIR)/$(MAIN).pdf . || true
	@echo "✓ Quick build complete"

# Use local LaTeX installation instead of Docker
local:
	@echo "Building with local LaTeX installation..."
	$(MAKE) all COMPILE_METHOD=local

# Clean auxiliary files
clean:
	rm -f $(SRC_DIR)/*.aux $(SRC_DIR)/*.log $(SRC_DIR)/*.out $(SRC_DIR)/*.toc $(SRC_DIR)/*.bbl $(SRC_DIR)/*.blg $(SRC_DIR)/*.synctex.gz
	rm -f $(SRC_DIR)/build-info.tex
	rm -rf $(BUILD_DIR)

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf $(SRC_DIR)/$(MAIN).pdf

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
	@echo "  make                 - Build PDF using Alpine Docker image (default)"
	@echo "  make docker-pull     - Download custom Alpine image (~500MB-1GB)"
	@echo "  make docker-pull-full - Download full TeXLive image (~4-5GB)"
	@echo "  make local           - Build using local LaTeX installation"
	@echo "  make quick           - Quick build without bibliography update"
	@echo "  make clean           - Remove auxiliary files"
	@echo "  make cleanall        - Remove all generated files including PDF"
	@echo "  make view            - Open the PDF"
	@echo "  make shell           - Open interactive Docker shell for debugging"
	@echo "  make help            - Show this help message"
	@echo ""
	@echo "First time setup:"
	@echo "  1. Install Docker: https://docs.docker.com/get-docker/"
	@echo "  2. Run: make docker-pull"
	@echo "  3. Run: make"
	@echo ""
	@echo "To use full TeXLive image instead of Alpine:"
	@echo "  DOCKER_IMAGE=texlive/texlive:latest make"
	@echo ""
	@echo "To use local LaTeX instead of Docker:"
	@echo "  make local"
	@echo ""
	@echo "Current Docker image: $(DOCKER_IMAGE)"
	@echo "Current method: $(COMPILE_METHOD)"
