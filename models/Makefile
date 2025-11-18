.PHONY: build test run sweep dev clean help motivation-scale motivation-threshold motivation-transition montecarlo-alignment ostrom-scale

# Default target
help:
	@echo "Coordination Trilemma - Computational Models"
	@echo ""
	@echo "Usage:"
	@echo "  make build    - Build Docker image"
	@echo "  make test     - Run quick test"
	@echo "  make run      - Run baseline ABM experiment"
	@echo "  make sweep    - Run parameter sweep (slow)"
	@echo "  make dev      - Start Jupyter development environment"
	@echo "  make clean    - Remove Docker images and containers"
	@echo ""
	@echo "Motivation Foundations (Appendix F):"
	@echo "  make motivation-scale      - Institutional vs soteriological at scale"
	@echo "  make motivation-threshold  - Find soteriological threshold for stability"
	@echo "  make motivation-transition - Bifurcation analysis at Dunbar scale"
	@echo "  make montecarlo-alignment  - Long-horizon alignment testing"
	@echo "  make ostrom-scale          - Ostrom polycentric governance at scale"
	@echo ""

# Build the Docker image
build:
	docker-compose build

# Run quick test
test: build
	docker-compose run --rm test

# Run baseline ABM experiment
run: build
	@mkdir -p ../figures/static ../data/simulations
	docker-compose run --rm abm

# Run parameter sweep
sweep: build
	@mkdir -p ../figures/static ../data/simulations
	docker-compose run --rm sweep

# Start development environment
dev: build
	@echo "Starting Jupyter Lab at http://localhost:8888"
	docker-compose up dev

# Clean up
clean:
	docker-compose down --rmi local --volumes --remove-orphans
	docker system prune -f

# Run with custom parameters
# Usage: make custom ARGS="--steps 500 --enforcers 200"
custom: build
	@mkdir -p ../figures/static ../data/simulations
	docker-compose run --rm abm python -m python.abm.corruption_dynamics $(ARGS)

# ============================================================================
# Motivation Foundations Model (Appendix F)
# Tests soteriological necessity hypothesis
# ============================================================================

# Demonstrate scale-dependent institutional degradation
# Shows: Institutional mechanisms fail beyond Dunbar, soteriological remains stable
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
