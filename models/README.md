# Computational Models for Coordination Trilemma

This directory contains the computational models that validate and extend the theoretical analysis in the Coordination Trilemma paper.

## Structure

```
models/
├── python/           # Python models and analysis
│   ├── abm/          # Agent-based models (mesa)
│   ├── game_theory/  # Game-theoretic solvers
│   ├── analysis/     # Statistical analysis
│   └── notebooks/    # Jupyter notebooks
├── go/               # Go simulations (performance-critical)
│   └── montecarlo/   # Monte Carlo cycle simulations
```

## Python Setup

```bash
cd models/python
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## Go Setup

```bash
cd models/go
go mod download
```

## Models

### 1. Corruption Dynamics ABM (`python/abm/corruption_dynamics.py`)

Agent-based model simulating enforcer corruption over time in hierarchical systems.

**Key parameters:**
- `n_enforcers`: Number of enforcement agents
- `integrity_dist`: Distribution of M_integrity values
- `extraction_opportunity`: U_e availability
- `detection_probability`: P_detection baseline

### 2. Cooperation Threshold Model (`python/abm/cooperation_threshold.py`)

Simulates critical mass dynamics for voluntary coordination.

**Key parameters:**
- `n_agents`: Population size
- `theta`: Proportion transformed
- `motivation_dist`: Distribution of M_trans
- `cooperation_cost`: c parameter

### 3. Monte Carlo Cycle Simulations (`go/montecarlo/`)

High-performance simulations of corruption-to-TCS cycles.

**Key parameters:**
- `cycle_duration`: λ (average cycle length)
- `p_ai`: Probability of AI-controlled TCS per cycle
- `n_simulations`: Number of Monte Carlo runs

### 4. Game-Theoretic Analysis (`python/game_theory/`)

Computation of Nash equilibria and evolutionary dynamics.

## Running Models

```bash
# Run corruption dynamics ABM
python -m abm.corruption_dynamics --config configs/baseline.yaml

# Run Monte Carlo simulations
cd go && go run ./montecarlo/main.go -n 1000000

# Generate figures
python -m analysis.generate_figures --output ../figures/
```

## Output

Results are saved to `../data/simulations/` and figures to `../figures/`.

## Testing

```bash
# Python tests
pytest python/

# Go tests
cd go && go test ./...
```

## Citation

If using these models, please cite the main paper.
