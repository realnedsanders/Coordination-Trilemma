# Makefile for Coordination Trilemma Computational Models
#
# This project uses two languages for different purposes:
# - Python: ABM simulations (Mesa), analysis, visualization (matplotlib/numpy)
# - Go: High-performance Monte Carlo simulations
#
# All models run in Docker containers for reproducibility.

.PHONY: help build clean test
.PHONY: all-figures all-simulations
.PHONY: python-abm python-corruption python-cooperation python-polycentric python-diagrams
.PHONY: go-montecarlo go-motivation go-ostrom
.PHONY: motivation-scale motivation-threshold motivation-transition montecarlo-alignment ostrom-scale

# ============================================================================
# Help & Common Targets
# ============================================================================

help:
	@echo "Coordination Trilemma - Computational Models"
	@echo ""
	@echo "Build & Test:"
	@echo "  make build              - Build all Docker images"
	@echo "  make test               - Run quick test"
	@echo "  make clean              - Remove Docker images and containers"
	@echo ""
	@echo "Generate All Outputs:"
	@echo "  make all-figures        - Generate all figures for the paper"
	@echo "  make all-simulations    - Run all simulation experiments"
	@echo ""
	@echo "Python ABM Models (Mesa/NumPy/Matplotlib):"
	@echo "  make python-abm         - Run all Python ABM simulations"
	@echo "  make python-corruption  - Corruption dynamics (Theorem 1.1)"
	@echo "  make python-cooperation - Cooperation threshold (Theorem 4.2)"
	@echo "  make python-polycentric - Polycentric governance comparison"
	@echo "  make python-diagrams    - Generate conceptual diagrams"
	@echo "  make python-sweep       - Parameter sensitivity sweep (slow)"
	@echo "  make python-dev         - Start Jupyter development environment"
	@echo ""
	@echo "Go High-Performance Models:"
	@echo "  make go-montecarlo      - Monte Carlo AI alignment simulation"
	@echo "  make go-motivation      - Motivation foundations model"
	@echo "  make go-ostrom          - Ostrom polycentric governance"
	@echo ""
	@echo "Appendix F - Motivation Foundations:"
	@echo "  make motivation-scale      - Institutional vs soteriological at scale"
	@echo "  make motivation-threshold  - Find soteriological threshold"
	@echo "  make motivation-transition - Bifurcation at Dunbar scale"
	@echo "  make montecarlo-alignment  - Long-horizon alignment testing"
	@echo "  make ostrom-scale          - Polycentric governance at scale"
	@echo ""

# Build all Docker images
build:
	docker-compose build

# Run quick test
test: build
	docker-compose run --rm test

# Clean up
clean:
	docker-compose down --rmi local --volumes --remove-orphans
	docker system prune -f

# ============================================================================
# Unified Targets - Generate All Outputs
# ============================================================================

# Generate all figures needed for the paper
all-figures: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "=== Generating All Figures ==="
	@echo ""
	@echo "--- Python ABM Figures ---"
	$(MAKE) python-corruption
	$(MAKE) python-cooperation
	$(MAKE) python-diagrams
	@echo ""
	@echo "=== All figures generated ==="

# Run all simulation experiments
all-simulations: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "=== Running All Simulations ==="
	$(MAKE) python-abm
	$(MAKE) go-montecarlo
	$(MAKE) go-motivation
	$(MAKE) go-ostrom
	@echo "=== All simulations complete ==="

# ============================================================================
# Python ABM Models
# Uses: Mesa, NumPy, Matplotlib, NetworkX
# Container: models (Dockerfile in this directory)
# ============================================================================

# Run all Python ABM simulations
python-abm: python-corruption python-cooperation python-polycentric

# Corruption dynamics - validates Theorem 1.1 (Corruption Inevitability)
python-corruption: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "Running corruption dynamics simulation..."
	docker-compose run --rm abm python -m python.abm.corruption_dynamics \
		--steps 200 --enforcers 100 --seed 42 --output /app/figures

# Cooperation threshold - validates Theorem 4.2 (Voluntary Cooperation)
python-cooperation: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "Running cooperation threshold simulation..."
	docker-compose run --rm cooperation
	@echo "Running bifurcation analysis..."
	docker-compose run --rm bifurcation

# Polycentric governance comparison
python-polycentric: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "Running polycentric governance comparison..."
	docker-compose run --rm ostrom

# Generate conceptual diagrams (static figures)
python-diagrams: build
	@mkdir -p ../figures/static
	@echo "Generating conceptual diagrams..."
	docker-compose run --rm abm python -m python.analysis.generate_diagrams \
		--all --output /app/figures

# Parameter sensitivity sweep (computationally intensive)
python-sweep: build
	@mkdir -p ../figures/static ../data/simulations
	@echo "Running parameter sweep (this may take a while)..."
	docker-compose run --rm sweep

# Development environment with Jupyter
python-dev: build
	@echo "Starting Jupyter Lab at http://localhost:8888"
	docker-compose up dev

# Custom Python run
# Usage: make python-custom ARGS="--steps 500 --enforcers 200"
python-custom: build
	@mkdir -p ../figures/static ../data/simulations
	docker-compose run --rm abm python -m python.abm.corruption_dynamics $(ARGS)

# ============================================================================
# Go High-Performance Models
# Uses: Standard library only (no external dependencies)
# Container: go (Dockerfile in go/ directory)
# ============================================================================

# Monte Carlo AI alignment simulation
go-montecarlo: build
	@mkdir -p ../data/simulations
	@echo "Running Monte Carlo alignment simulation..."
	docker-compose run --rm montecarlo

# Motivation foundations model
go-motivation: build
	@mkdir -p ../data/simulations
	@echo "Running motivation foundations model..."
	docker-compose run --rm motivation

# Ostrom polycentric governance (Go implementation)
go-ostrom: build
	@mkdir -p ../data/simulations
	@echo "Running Ostrom model..."
	docker-compose run --rm ostrom-go

# ============================================================================
# Appendix F - Motivation Foundations Experiments
# Tests soteriological necessity hypothesis
# ============================================================================

# Demonstrate scale-dependent institutional degradation
motivation-scale: build
	@echo "=== Scale Effects: Institutional vs Soteriological ==="
	@echo ""
	@echo "--- PURE INSTITUTIONAL (0% soteriological) ---"
	@for n in 150 300 1000 10000; do \
		echo ""; \
		echo "N=$$n:"; \
		docker-compose run --rm motivation -n $$n -steps 500 -reps 30 -soterio-frac 0.0 \
			-cost 1.3 -benefit 1.2 -network 0.3 \
			-scale-effects=true -optimal-scale 150 -scale-decay 1.0 -workers 8; \
	done
	@echo ""
	@echo "--- PURE SOTERIOLOGICAL (100%) ---"
	@for n in 150 1000 10000; do \
		echo ""; \
		echo "N=$$n:"; \
		docker-compose run --rm motivation -n $$n -steps 500 -reps 30 -soterio-frac 1.0 \
			-cost 1.3 -benefit 1.2 -network 0.3 \
			-scale-effects=true -optimal-scale 150 -scale-decay 1.0 -workers 8; \
	done

# Find minimum soteriological fraction for stable cooperation at scale
motivation-threshold: build
	@echo "=== Soteriological Threshold at N=1000 ==="
	@echo "Finding minimum fraction for stable cooperation"
	@for frac in 0.0 0.1 0.2 0.3 0.4 0.5; do \
		echo ""; \
		echo "Soteriological fraction: $$frac"; \
		docker-compose run --rm motivation -n 1000 -steps 500 -reps 30 -soterio-frac $$frac \
			-cost 1.3 -benefit 1.2 -network 0.3 \
			-scale-effects=true -optimal-scale 150 -scale-decay 1.0 -workers 8; \
	done

# Bifurcation analysis showing transition at ~1.5x Dunbar
motivation-transition: build
	@echo "=== Institutional Transition Point ==="
	@echo "Bimodal behavior emerges at 1.2-1.7x Dunbar scale"
	@for n in 150 175 200 225 250 300; do \
		echo ""; \
		echo "N=$$n:"; \
		docker-compose run --rm motivation -n $$n -steps 500 -reps 30 -soterio-frac 0.0 \
			-cost 1.3 -benefit 1.2 -network 0.3 \
			-scale-effects=true -optimal-scale 150 -scale-decay 1.0 -workers 8; \
	done

# Long-horizon alignment testing (Monte Carlo)
montecarlo-alignment: build
	@echo "=== Monte Carlo Alignment Testing ==="
	@echo "Testing alignment robustness over extended time horizons"
	@for align in 0.95 0.99 0.999; do \
		echo ""; \
		echo "Alignment probability: $$align (10,000 year horizon)"; \
		docker-compose run --rm montecarlo \
			-n 100000 -p-ai $$align -max-time 10000 -cycle 50 -cycle-std 20 -growth 0.1; \
	done

# Ostrom polycentric governance at scale
ostrom-scale: build
	@echo "=== Ostrom Model Scale Testing ==="
	@echo "Testing polycentric governance with scale-dependent degradation"
	@for groups in 50 20 10 5; do \
		n=$$((groups * 20)); \
		echo ""; \
		echo "N=$$n ($$groups groups of 20):"; \
		docker-compose run --rm ostrom-go -n $$n -groups $$groups -steps 200 -reps 30 \
			-scale-effects=true -optimal-size 20; \
	done
