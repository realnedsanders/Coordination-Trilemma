# Makefile for Coordination Trilemma LaTeX document
# Uses Docker by default (no local LaTeX installation needed)

# Source directories
SRC_DIR = src/tex
SCRIPTS_DIR = scripts
BUILD_DIR = build
MODELS_DIR = models
FIGURES_DIR = figures/static

# Main tex file (in src/tex/)
MAIN = main
# Bibliography file
BIB = references

# Figure source files (for dependency tracking)
PYTHON_ABM_SOURCES = $(wildcard $(MODELS_DIR)/python/abm/*.py)
PYTHON_ANALYSIS_SOURCES = $(wildcard $(MODELS_DIR)/python/analysis/*.py)
GO_SOURCES = $(wildcard $(MODELS_DIR)/go/*/*.go)
MODEL_SOURCES = $(PYTHON_ABM_SOURCES) $(PYTHON_ANALYSIS_SOURCES) $(GO_SOURCES)

# Generated figures (core set that can be built without Monte Carlo data)
GENERATED_FIGURES = \
	$(FIGURES_DIR)/corruption_dynamics.png \
	$(FIGURES_DIR)/bifurcation_analysis.png \
	$(FIGURES_DIR)/coordination_trilemma.png \
	$(FIGURES_DIR)/default_trajectory_state_machine.png \
	$(FIGURES_DIR)/scale_degradation_curves.png \
	$(FIGURES_DIR)/enforcement_regress.png \
	$(FIGURES_DIR)/detection_timeline.png \
	$(FIGURES_DIR)/longevity_scatter.png

# Optional figures that require Monte Carlo simulation data
OPTIONAL_FIGURES = \
	$(FIGURES_DIR)/scenario_comparison.png

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
# Auto-detect GitHub Actions and use local compilation (container already provides LaTeX)
ifdef GITHUB_ACTIONS
    COMPILE_METHOD ?= local
else
    COMPILE_METHOD ?= docker
endif

# Set commands based on compilation method
ifeq ($(COMPILE_METHOD),local)
    RUN_LATEX = cd $(SRC_DIR) && $(LATEX)
    RUN_BIBTEX = cd $(SRC_DIR) && $(BIBTEX)
else
    RUN_LATEX = $(DOCKER_RUN) $(LATEX)
    RUN_BIBTEX = $(DOCKER_RUN) $(BIBTEX)
endif

.PHONY: all clean cleanall clean-figures view docker-pull docker-pull-full help local figures figures-force
.PHONY: models models-test models-help models-clean

# Default target
# In GitHub Actions, figures are generated in a separate job, so skip here
ifdef GITHUB_ACTIONS
all: $(BUILD_DIR) $(MAIN).pdf clean
else
all: $(BUILD_DIR) figures $(MAIN).pdf clean
endif

# Ensure build directory exists
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

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

# ============================================================================
# Figure Generation
# ============================================================================

# Ensure figures directory exists
$(FIGURES_DIR):
	@mkdir -p $(FIGURES_DIR)

# Marker file to track when containers were last built
$(BUILD_DIR)/.models-built: $(MODEL_SOURCES) | $(BUILD_DIR)
	@echo "Building model containers..."
	cd $(MODELS_DIR) && $(MAKE) build
	@touch $@

# Generate all figures (only if source files changed)
figures: $(FIGURES_DIR) $(GENERATED_FIGURES)
	@echo "✓ All figures up to date"

# Force regenerate all figures
figures-force: $(BUILD_DIR)/.models-built
	@echo "Force regenerating all figures..."
	cd $(MODELS_DIR) && docker-compose run --rm abm python -m python.abm.corruption_dynamics --steps 200 --enforcers 100 --seed 42 --output /app/figures
	cd $(MODELS_DIR) && docker-compose run --rm bifurcation python -m python.abm.cooperation_threshold --bifurcation --steps 100 --agents 500 --output /app/figures
	cd $(MODELS_DIR) && docker-compose run --rm abm python -m python.analysis.generate_diagrams --all --output /app/figures
	@echo "✓ All figures regenerated"

# ABM simulation figures - depend on Python ABM sources and built containers
$(FIGURES_DIR)/corruption_dynamics.png: $(PYTHON_ABM_SOURCES) $(BUILD_DIR)/.models-built | $(FIGURES_DIR)
	@echo "Generating corruption dynamics figure..."
	cd $(MODELS_DIR) && docker-compose run --rm abm python -m python.abm.corruption_dynamics --steps 200 --enforcers 100 --seed 42 --output /app/figures

$(FIGURES_DIR)/bifurcation_analysis.png: $(PYTHON_ABM_SOURCES) $(BUILD_DIR)/.models-built | $(FIGURES_DIR)
	@echo "Generating bifurcation analysis figure..."
	cd $(MODELS_DIR) && docker-compose run --rm bifurcation python -m python.abm.cooperation_threshold --bifurcation --steps 100 --agents 500 --output /app/figures

# Conceptual diagrams - depend on generate_diagrams.py and built containers
$(FIGURES_DIR)/coordination_trilemma.png $(FIGURES_DIR)/default_trajectory_state_machine.png $(FIGURES_DIR)/scale_degradation_curves.png $(FIGURES_DIR)/enforcement_regress.png $(FIGURES_DIR)/detection_timeline.png $(FIGURES_DIR)/longevity_scatter.png: $(MODELS_DIR)/python/analysis/generate_diagrams.py $(BUILD_DIR)/.models-built | $(FIGURES_DIR)
	@echo "Generating conceptual diagrams..."
	cd $(MODELS_DIR) && docker-compose run --rm abm python -m python.analysis.generate_diagrams --all --output /app/figures

# ============================================================================
# Build Information
# ============================================================================

# Generate build information from git metadata
$(BUILD_DIR)/build-info.tex: | $(BUILD_DIR)
	@echo "Generating build information..."
	@$(SCRIPTS_DIR)/generate-build-info.sh
	@mv build-info.tex $(BUILD_DIR)/ 2>/dev/null || true

# Full build with bibliography
# In GitHub Actions, figures are pre-generated, so don't list as dependency
ifdef GITHUB_ACTIONS
$(MAIN).pdf: $(BUILD_DIR)/build-info.tex $(SRC_DIR)/$(MAIN).tex $(SRC_DIR)/main-article.tex $(SRC_DIR)/appendices/*.tex $(SRC_DIR)/$(BIB).bib $(SRC_DIR)/glossary.tex
else
$(MAIN).pdf: $(BUILD_DIR)/build-info.tex $(SRC_DIR)/$(MAIN).tex $(SRC_DIR)/main-article.tex $(SRC_DIR)/appendices/*.tex $(SRC_DIR)/$(BIB).bib $(SRC_DIR)/glossary.tex $(GENERATED_FIGURES)
endif
	@echo "Compiling with $(COMPILE_METHOD) method..."
	@cp $(BUILD_DIR)/build-info.tex $(SRC_DIR)/ || true
	$(RUN_LATEX) $(MAIN)
	$(RUN_BIBTEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	$(RUN_LATEX) $(MAIN)
	@mv $(SRC_DIR)/$(MAIN).pdf . || true
	@echo "✓ PDF generated: $(MAIN).pdf"

# Use local LaTeX installation instead of Docker
local:
	@echo "Building with local LaTeX installation..."
	$(MAKE) all COMPILE_METHOD=local

# Clean auxiliary files
clean:
	rm -f $(SRC_DIR)/*.aux $(SRC_DIR)/*.log $(SRC_DIR)/*.out $(SRC_DIR)/*.toc $(SRC_DIR)/*.bbl $(SRC_DIR)/*.blg $(SRC_DIR)/*.synctex.gz
	rm -f $(SRC_DIR)/build-info.tex
	rm -rf $(BUILD_DIR)

# Clean everything including PDF and generated figures
cleanall: clean
	rm -f $(MAIN).pdf
	rm -f $(FIGURES_DIR)/*.png $(FIGURES_DIR)/*.csv
	rm -rf data/simulations/

# Clean only figures (useful for forcing regeneration)
clean-figures:
	rm -f $(FIGURES_DIR)/*.png $(FIGURES_DIR)/*.csv
	@echo "Figures cleaned. Run 'make figures' to regenerate."

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

# ============================================================================
# Computational Models (Python ABM + Go Monte Carlo)
# ============================================================================

# Build model containers
models: $(BUILD_DIR)/.models-built
	@echo "✓ Model containers up to date"

# Run model tests
models-test:
	cd $(MODELS_DIR) && $(MAKE) test

# Show model help
models-help:
	cd $(MODELS_DIR) && $(MAKE) help

# Clean model containers
models-clean:
	cd $(MODELS_DIR) && $(MAKE) clean

# Help message
help:
	@echo "Coordination Trilemma LaTeX Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make                 - Build PDF with figures using Docker (default)"
	@echo "  make figures         - Generate figures only (with dependency tracking)"
	@echo "  make figures-force   - Force regenerate all figures"
	@echo "  make docker-pull     - Download custom Alpine image (~500MB-1GB)"
	@echo "  make docker-pull-full - Download full TeXLive image (~4-5GB)"
	@echo "  make local           - Build using local LaTeX installation"
	@echo "  make clean           - Remove auxiliary files"
	@echo "  make cleanall        - Remove all generated files including PDF"
	@echo "  make view            - Open the PDF"
	@echo "  make shell           - Open interactive Docker shell for debugging"
	@echo "  make help            - Show this help message"
	@echo ""
	@echo "Computational models:"
	@echo "  make models          - Build model containers"
	@echo "  make models-test     - Run model tests"
	@echo "  make models-help     - Show detailed model targets"
	@echo "  make models-clean    - Clean model containers"
	@echo ""
	@echo "First time setup:"
	@echo "  1. Install Docker: https://docs.docker.com/get-docker/"
	@echo "  2. Run: make docker-pull"
	@echo "  3. Run: make"
	@echo ""
	@echo "Figure generation:"
	@echo "  Figures are automatically generated when model source files change."
	@echo "  Use 'make figures-force' to regenerate all figures from scratch."
	@echo ""
	@echo "To use full TeXLive image instead of Alpine:"
	@echo "  DOCKER_IMAGE=texlive/texlive:latest make"
	@echo ""
	@echo "To use local LaTeX instead of Docker:"
	@echo "  make local"
	@echo ""
	@echo "Current Docker image: $(DOCKER_IMAGE)"
	@echo "Current method: $(COMPILE_METHOD)"
