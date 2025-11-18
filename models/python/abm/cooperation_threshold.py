"""
Cooperation Threshold Agent-Based Model

This model validates Theorem 4.2 (Voluntary Cooperation Stability) by simulating
the critical mass dynamics of voluntary coordination.

Key dynamics:
- Agents have intrinsic motivation M_i to cooperate
- Cooperation cost c, benefit from k cooperators: β*k/n
- Cooperation is rational when: M_i > c - β*k/n
- Critical mass θ_crit determines stability
- Network effects can reinforce cooperation above threshold
"""

import numpy as np
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from typing import Optional
from concurrent.futures import ProcessPoolExecutor
import os
import yaml


class Citizen(Agent):
    """
    A citizen who decides whether to cooperate or defect.

    Attributes:
        motivation: Intrinsic motivation M_i to cooperate
        cooperating: Current cooperation status
        transformed: Whether agent has undergone value transformation
    """

    def __init__(self, model: "CooperationModel", motivation: float, transformed: bool = False):
        super().__init__(model)
        self.base_motivation = motivation
        self.motivation = motivation
        self.cooperating = False
        self.transformed = transformed

    def step(self):
        """
        Decide whether to cooperate based on payoffs and motivation.

        Cooperation rational when:
        M_i > c - β * (k/n)

        Where k = current number of cooperators
        """
        # Get current cooperation level
        n = len(self.model.agents)
        k = sum(1 for a in self.model.agents if a.cooperating)
        cooperation_rate = k / n if n > 0 else 0

        # Calculate threshold for cooperation
        # From Theorem 4.2: cooperate if M_i > c - β*θ
        threshold = self.model.cooperation_cost - self.model.benefit_multiplier * cooperation_rate

        # Network effects: seeing others cooperate boosts motivation
        if self.model.network_effects:
            social_boost = self.model.network_strength * cooperation_rate
            effective_motivation = self.motivation + social_boost
        else:
            effective_motivation = self.motivation

        # Decision with some noise (bounded rationality)
        noise = np.random.normal(0, self.model.decision_noise)
        self.cooperating = (effective_motivation + noise) > threshold

        # Update motivation based on experience
        if self.model.motivation_dynamics:
            self._update_motivation(cooperation_rate)

    def _update_motivation(self, cooperation_rate: float):
        """
        Motivation can change based on social environment.

        - Positive reinforcement when cooperating in cooperative environment
        - Negative when cooperating alone (sucker's payoff discouragement)
        """
        if self.cooperating:
            if cooperation_rate > 0.5:
                # Cooperation reinforced in cooperative environment
                self.motivation = min(
                    self.motivation * (1 + self.model.reinforcement_rate),
                    self.base_motivation * 2  # Cap at 2x base
                )
            else:
                # Discouragement when cooperating alone
                self.motivation *= (1 - self.model.discouragement_rate)
        else:
            # Gradual return to base motivation when defecting
            self.motivation = self.motivation * 0.99 + self.base_motivation * 0.01


class CooperationModel(Model):
    """
    Model of cooperation dynamics with critical mass threshold.

    Validates Theorem 4.2: cooperation is stable when θ > θ_crit

    Parameters:
        n_agents: Number of agents
        cooperation_cost: Cost c of cooperating
        benefit_multiplier: β - social benefit multiplier
        motivation_mean: Mean of motivation distribution
        motivation_std: Std dev of motivation distribution
        initial_cooperation: Starting cooperation rate
        transformed_fraction: Fraction with boosted motivation (value-transformed)
        transformation_boost: How much transformation increases motivation
        network_effects: Whether to model social proof effects
        network_strength: Strength of network effects
        motivation_dynamics: Whether motivation changes over time
        reinforcement_rate: Rate of positive reinforcement
        discouragement_rate: Rate of discouragement
        decision_noise: Noise in decision making
        seed: Random seed
    """

    def __init__(
        self,
        n_agents: int = 1000,
        cooperation_cost: float = 1.0,
        benefit_multiplier: float = 2.0,
        motivation_mean: float = 0.5,
        motivation_std: float = 0.3,
        initial_cooperation: float = 0.5,
        transformed_fraction: float = 0.0,
        transformation_boost: float = 1.0,
        network_effects: bool = True,
        network_strength: float = 0.5,
        motivation_dynamics: bool = True,
        reinforcement_rate: float = 0.02,
        discouragement_rate: float = 0.01,
        decision_noise: float = 0.1,
        seed: Optional[int] = None
    ):
        super().__init__(seed=seed)

        if seed is not None:
            np.random.seed(seed)

        # Model parameters
        self.n_agents = n_agents
        self.cooperation_cost = cooperation_cost
        self.benefit_multiplier = benefit_multiplier
        self.motivation_mean = motivation_mean
        self.motivation_std = motivation_std
        self.network_effects = network_effects
        self.network_strength = network_strength
        self.motivation_dynamics = motivation_dynamics
        self.reinforcement_rate = reinforcement_rate
        self.discouragement_rate = discouragement_rate
        self.decision_noise = decision_noise

        # Calculate theoretical critical mass
        # θ_crit = c / (β + M̄)
        self.theta_crit = cooperation_cost / (benefit_multiplier + motivation_mean)

        # Create agents
        n_transformed = int(n_agents * transformed_fraction)

        for i in range(n_agents):
            # Draw motivation from distribution
            base_motivation = max(0, np.random.normal(motivation_mean, motivation_std))

            # Apply transformation boost to some agents
            if i < n_transformed:
                motivation = base_motivation + transformation_boost
                transformed = True
            else:
                motivation = base_motivation
                transformed = False

            agent = Citizen(self, motivation, transformed)

            # Set initial cooperation status
            agent.cooperating = np.random.random() < initial_cooperation

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Cooperation_Rate": lambda m: self._cooperation_rate(),
                "Mean_Motivation": lambda m: self._mean_motivation(),
                "Theta_Crit": lambda m: m.theta_crit,
                "Above_Threshold": lambda m: self._cooperation_rate() > m.theta_crit,
                "Std_Motivation": lambda m: np.std([a.motivation for a in m.agents]),
            },
            agent_reporters={
                "Motivation": "motivation",
                "Cooperating": "cooperating",
                "Transformed": "transformed",
            }
        )

    def _cooperation_rate(self) -> float:
        """Current proportion of cooperators."""
        if self.n_agents == 0:
            return 0.0
        return sum(1 for a in self.agents if a.cooperating) / self.n_agents

    def _mean_motivation(self) -> float:
        """Average motivation across agents."""
        if self.n_agents == 0:
            return 0.0
        return np.mean([a.motivation for a in self.agents])

    def step(self):
        """Advance model by one step."""
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

    def run(self, steps: int = 100) -> None:
        """Run model for specified number of steps."""
        for _ in range(steps):
            self.step()


def run_experiment(config_path: str = None, **kwargs) -> dict:
    """
    Run a cooperation threshold experiment.

    Args:
        config_path: Path to YAML config file
        **kwargs: Override config parameters

    Returns:
        Dictionary with model results
    """
    # Load config if provided
    if config_path:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    # Override with kwargs
    config.update(kwargs)

    # Set defaults
    n_steps = config.pop("n_steps", 100)

    # Create and run model
    model = CooperationModel(**config)
    model.run(n_steps)

    # Get results
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    return {
        "model_data": model_data,
        "agent_data": agent_data,
        "final_cooperation_rate": model._cooperation_rate(),
        "final_mean_motivation": model._mean_motivation(),
        "theta_crit": model.theta_crit,
        "stable": model._cooperation_rate() > model.theta_crit,
        "config": config,
    }


def _run_single_bifurcation(args: tuple) -> dict:
    """
    Worker function for parallel bifurcation analysis.

    Args:
        args: Tuple of (init_rate, rep, n_steps, model_params)

    Returns:
        Dictionary with single run results
    """
    init_rate, rep, n_steps, model_params = args

    model = CooperationModel(
        initial_cooperation=init_rate,
        seed=rep,
        **model_params
    )
    model.run(n_steps)

    return {
        "initial_rate": init_rate,
        "final_rate": model._cooperation_rate(),
        "theta_crit": model.theta_crit,
        "replication": rep,
    }


def run_bifurcation_analysis(
    initial_rates: list = None,
    n_replications: int = 5,
    n_steps: int = 100,
    n_workers: int = None,
    **model_params
) -> dict:
    """
    Run bifurcation analysis to find critical threshold.

    Tests different initial cooperation rates to find
    which converge to cooperation vs defection equilibrium.

    Args:
        initial_rates: List of initial cooperation rates to test
        n_replications: Replications per initial rate
        n_steps: Steps per run
        n_workers: Number of parallel workers (default: CPU count)
        **model_params: Parameters for CooperationModel

    Returns:
        Dictionary with bifurcation results
    """
    if initial_rates is None:
        initial_rates = np.linspace(0.1, 0.9, 17)

    if n_workers is None:
        n_workers = os.cpu_count() or 4

    # Create all job arguments
    jobs = [
        (init_rate, rep, n_steps, model_params)
        for init_rate in initial_rates
        for rep in range(n_replications)
    ]

    # Run in parallel
    if n_workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = list(executor.map(_run_single_bifurcation, jobs))
    else:
        # Sequential fallback
        results = [_run_single_bifurcation(job) for job in jobs]

    return {
        "results": results,
        "theta_crit": results[0]["theta_crit"] if results else None,
    }


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description="Run cooperation threshold ABM")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--steps", type=int, default=100, help="Number of steps")
    parser.add_argument("--agents", type=int, default=1000, help="Number of agents")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, help="Output directory for figures")
    parser.add_argument("--bifurcation", action="store_true", help="Run bifurcation analysis")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel workers (default: CPU count)")
    parser.add_argument("--reps", type=int, default=5, help="Number of replications per initial rate")

    args = parser.parse_args()

    if args.bifurcation:
        # Run bifurcation analysis
        n_workers = args.workers or os.cpu_count() or 4
        print(f"Running bifurcation analysis with {n_workers} workers...")
        bifurc = run_bifurcation_analysis(
            n_agents=args.agents,
            n_steps=args.steps,
            n_replications=args.reps,
            n_workers=n_workers
        )

        # Plot bifurcation diagram
        fig, ax = plt.subplots(figsize=(10, 6))

        initial_rates = [r["initial_rate"] for r in bifurc["results"]]
        final_rates = [r["final_rate"] for r in bifurc["results"]]

        ax.scatter(initial_rates, final_rates, alpha=0.5, s=20)
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label="No change")

        # Mark critical threshold
        theta_crit = bifurc["theta_crit"]
        ax.axvline(x=theta_crit, color='r', linestyle='--',
                   label=f"θ_crit = {theta_crit:.2f}")
        ax.axhline(y=theta_crit, color='r', linestyle='--', alpha=0.5)

        ax.set_xlabel("Initial Cooperation Rate", fontsize=12)
        ax.set_ylabel("Final Cooperation Rate", fontsize=12)
        ax.set_title("Bifurcation Analysis: Critical Mass Threshold", fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if args.output:
            plt.savefig(f"{args.output}/bifurcation_analysis.png", dpi=150)
        else:
            plt.show()

        print(f"Critical threshold θ_crit = {theta_crit:.3f}")

    else:
        # Run single experiment
        results = run_experiment(
            config_path=args.config,
            n_agents=args.agents,
            n_steps=args.steps,
            seed=args.seed
        )

        print(f"Final cooperation rate: {results['final_cooperation_rate']:.2%}")
        print(f"Critical threshold θ_crit: {results['theta_crit']:.3f}")
        print(f"Stable cooperation: {results['stable']}")

        # Plot results
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Cooperation rate over time
        ax = axes[0, 0]
        ax.plot(results["model_data"]["Cooperation_Rate"])
        ax.axhline(y=results["theta_crit"], color='r', linestyle='--',
                   label=f"θ_crit = {results['theta_crit']:.2f}")
        ax.set_xlabel("Step")
        ax.set_ylabel("Cooperation Rate")
        ax.set_title("Cooperation Rate Over Time")
        ax.legend()

        # Mean motivation over time
        ax = axes[0, 1]
        ax.plot(results["model_data"]["Mean_Motivation"])
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean Motivation")
        ax.set_title("Mean Motivation Over Time")

        # Final motivation distribution
        ax = axes[1, 0]
        final_step = results["agent_data"].index.get_level_values(0).max()
        final_motivations = results["agent_data"].loc[final_step, "Motivation"]
        ax.hist(final_motivations, bins=30, edgecolor='black', alpha=0.7)
        ax.axvline(x=results["config"].get("cooperation_cost", 1.0), color='r',
                   linestyle='--', label=f"Cost c = {results['config'].get('cooperation_cost', 1.0)}")
        ax.set_xlabel("Motivation")
        ax.set_ylabel("Count")
        ax.set_title("Final Motivation Distribution")
        ax.legend()

        # Cooperation status by motivation
        ax = axes[1, 1]
        final_coop = results["agent_data"].loc[final_step, "Cooperating"]
        cooperators = final_motivations[final_coop == True]
        defectors = final_motivations[final_coop == False]
        ax.hist([cooperators, defectors], bins=20, label=["Cooperators", "Defectors"],
                edgecolor='black', alpha=0.7)
        ax.set_xlabel("Motivation")
        ax.set_ylabel("Count")
        ax.set_title("Motivation by Cooperation Status")
        ax.legend()

        plt.tight_layout()

        if args.output:
            plt.savefig(f"{args.output}/cooperation_threshold.png", dpi=150)
        else:
            plt.show()
