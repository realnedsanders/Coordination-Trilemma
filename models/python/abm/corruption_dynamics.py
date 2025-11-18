"""
Corruption Dynamics Agent-Based Model

This model simulates the emergence and spread of corruption in hierarchical
enforcement systems, validating Theorem 1.1 (Coordination Trilemma) and
the corruption inevitability claims from Appendix B.

Key dynamics:
- Enforcers have integrity motivation M_integrity (drawn from distribution)
- Extraction opportunities U_e arise stochastically
- Detection probability P_detection depends on oversight structure
- Corruption occurs when: U_e > cost_detection * P_detection + M_integrity
"""

import numpy as np
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from typing import Optional
import yaml


class Enforcer(Agent):
    """
    An enforcement agent who may become corrupt.

    Attributes:
        integrity: Base integrity motivation M_integrity
        corrupted: Whether agent has engaged in corruption
        extraction_events: Number of times agent has extracted
        oversight_level: How much oversight this agent receives (0-1)
    """

    def __init__(self, model: "CorruptionModel",
                 integrity: float, oversight_level: float):
        super().__init__(model)
        self.integrity = integrity
        self.corrupted = False
        self.extraction_events = 0
        self.oversight_level = oversight_level

    def step(self):
        """
        Each step, agent faces potential extraction opportunity.

        Decision rule from paper:
        Extract if U_e > cost_detection * P_detection + M_integrity
        """
        # Extraction opportunity (varies by step)
        extraction_opportunity = self.model.get_extraction_opportunity(self)

        if extraction_opportunity <= 0:
            return

        # Detection probability based on oversight
        detection_prob = self.model.base_detection_prob * self.oversight_level

        # Cost if detected (reputation, punishment)
        detection_cost = self.model.detection_cost

        # Expected cost of extraction
        expected_cost = detection_cost * detection_prob

        # Decision: extract if benefit exceeds expected cost + integrity
        if extraction_opportunity > expected_cost + self.integrity:
            self.corrupted = True
            self.extraction_events += 1

            # Corruption can reduce integrity over time (moral decay)
            if self.model.integrity_decay:
                self.integrity *= (1 - self.model.integrity_decay_rate)

            # Corruption can spread (seeing others corrupt reduces integrity)
            if self.model.corruption_contagion:
                self._spread_corruption()
        else:
            # Stayed honest this step - potential integrity reinforcement
            if self.model.integrity_reinforcement:
                # Get current corruption rate
                corruption_rate = sum(1 for a in self.model.agents if a.corrupted) / len(self.model.agents)

                # Reputation boost for staying honest in corrupt environment
                if corruption_rate > 0.3:
                    reputation_boost = self.model.reinforcement_rate * corruption_rate
                    self.integrity = min(
                        self.integrity * (1 + reputation_boost),
                        self.model.integrity_mean * 2  # Cap at 2x initial mean
                    )

    def _spread_corruption(self):
        """Corruption observability reduces others' integrity."""
        # Get nearby agents (in network or random sample)
        all_agents = list(self.model.agents)
        sample_size = min(5, len(all_agents) - 1)
        if sample_size > 0:
            others = self.model.random.sample(all_agents, sample_size)

            for other in others:
                if other != self and not other.corrupted:
                    # Reduce integrity slightly when observing corruption
                    other.integrity *= (1 - self.model.contagion_rate)


class CorruptionModel(Model):
    """
    Model of corruption emergence in enforcement hierarchies.

    Parameters:
        n_enforcers: Number of enforcement agents
        integrity_mean: Mean of integrity distribution
        integrity_std: Std dev of integrity distribution
        extraction_mean: Mean extraction opportunity per step
        extraction_std: Std dev of extraction opportunities
        base_detection_prob: Baseline detection probability
        detection_cost: Cost if corruption detected
        oversight_structure: 'flat', 'hierarchical', or 'none'
        integrity_decay: Whether corruption reduces integrity
        integrity_decay_rate: Rate of integrity decay per extraction
        corruption_contagion: Whether corruption spreads
        contagion_rate: Rate of contagion effect
        seed: Random seed for reproducibility
    """

    def __init__(
        self,
        n_enforcers: int = 100,
        integrity_mean: float = 5.0,
        integrity_std: float = 2.0,
        extraction_mean: float = 3.0,
        extraction_std: float = 1.5,
        base_detection_prob: float = 0.3,
        detection_cost: float = 10.0,
        oversight_structure: str = "hierarchical",
        integrity_decay: bool = True,
        integrity_decay_rate: float = 0.05,
        corruption_contagion: bool = True,
        contagion_rate: float = 0.02,
        integrity_reinforcement: bool = False,
        reinforcement_rate: float = 0.02,
        seed: Optional[int] = None
    ):
        super().__init__(seed=seed)

        if seed is not None:
            np.random.seed(seed)

        # Model parameters
        self.n_enforcers = n_enforcers
        self.integrity_mean = integrity_mean
        self.integrity_std = integrity_std
        self.extraction_mean = extraction_mean
        self.extraction_std = extraction_std
        self.base_detection_prob = base_detection_prob
        self.detection_cost = detection_cost
        self.oversight_structure = oversight_structure
        self.integrity_decay = integrity_decay
        self.integrity_decay_rate = integrity_decay_rate
        self.corruption_contagion = corruption_contagion
        self.contagion_rate = contagion_rate
        self.integrity_reinforcement = integrity_reinforcement
        self.reinforcement_rate = reinforcement_rate

        # Create agents with oversight levels based on structure
        oversight_levels = self._get_oversight_levels()

        for i in range(n_enforcers):
            # Draw integrity from truncated normal (must be positive)
            integrity = max(0.1, np.random.normal(integrity_mean, integrity_std))

            agent = Enforcer(self, integrity, oversight_levels[i])
            # Agent is automatically added to model.agents

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Corruption_Rate": lambda m: self._corruption_rate(),
                "Mean_Integrity": lambda m: self._mean_integrity(),
                "Total_Extractions": lambda m: self._total_extractions(),
                "Corrupted_Agents": lambda m: sum(1 for a in m.agents if a.corrupted),
            },
            agent_reporters={
                "Integrity": "integrity",
                "Corrupted": "corrupted",
                "Extractions": "extraction_events",
            }
        )

    def _get_oversight_levels(self) -> list[float]:
        """
        Assign oversight levels based on structure.

        - flat: Everyone has same oversight
        - hierarchical: Top levels have less oversight (infinite regress problem)
        - none: No oversight (P_detection = 0)
        """
        if self.oversight_structure == "flat":
            return [0.8] * self.n_enforcers

        elif self.oversight_structure == "hierarchical":
            # Top 10% have minimal oversight, bottom 50% have maximum
            levels = []
            for i in range(self.n_enforcers):
                rank = i / self.n_enforcers
                if rank < 0.1:  # Top 10% - minimal oversight
                    levels.append(0.1)
                elif rank < 0.3:  # Next 20%
                    levels.append(0.4)
                elif rank < 0.5:  # Middle
                    levels.append(0.6)
                else:  # Bottom 50% - maximum oversight
                    levels.append(0.9)
            return levels

        elif self.oversight_structure == "none":
            return [0.0] * self.n_enforcers

        else:
            raise ValueError(f"Unknown oversight structure: {self.oversight_structure}")

    def get_extraction_opportunity(self, agent: Enforcer) -> float:
        """
        Get extraction opportunity for an agent this step.

        Higher-ranked agents (lower oversight) have more opportunities.
        """
        base = np.random.normal(self.extraction_mean, self.extraction_std)

        # Scale by inverse of oversight (more power = more opportunity)
        power_multiplier = 1 + (1 - agent.oversight_level)

        return max(0, base * power_multiplier)

    def _corruption_rate(self) -> float:
        """Proportion of agents who have corrupted."""
        if self.n_enforcers == 0:
            return 0.0
        return sum(1 for a in self.agents if a.corrupted) / self.n_enforcers

    def _mean_integrity(self) -> float:
        """Average integrity across all agents."""
        if self.n_enforcers == 0:
            return 0.0
        return np.mean([a.integrity for a in self.agents])

    def _total_extractions(self) -> int:
        """Total extraction events across all agents."""
        return sum(a.extraction_events for a in self.agents)

    def step(self):
        """Advance model by one step."""
        self.datacollector.collect(self)
        # In Mesa 3.x, agents are activated via the agents attribute
        self.agents.shuffle_do("step")

    def run(self, steps: int = 100) -> None:
        """Run model for specified number of steps."""
        for _ in range(steps):
            self.step()


def run_experiment(config_path: str = None, **kwargs) -> dict:
    """
    Run a corruption dynamics experiment.

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
    n_steps = config.pop("n_steps", 200)

    # Create and run model
    model = CorruptionModel(**config)
    model.run(n_steps)

    # Get results
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()

    return {
        "model_data": model_data,
        "agent_data": agent_data,
        "final_corruption_rate": model._corruption_rate(),
        "final_mean_integrity": model._mean_integrity(),
        "total_extractions": model._total_extractions(),
        "config": config,
    }


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description="Run corruption dynamics ABM")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--steps", type=int, default=200, help="Number of steps")
    parser.add_argument("--enforcers", type=int, default=100, help="Number of enforcers")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, help="Output directory for figures")

    args = parser.parse_args()

    # Run experiment
    results = run_experiment(
        config_path=args.config,
        n_enforcers=args.enforcers,
        n_steps=args.steps,
        seed=args.seed
    )

    print(f"Final corruption rate: {results['final_corruption_rate']:.2%}")
    print(f"Final mean integrity: {results['final_mean_integrity']:.2f}")
    print(f"Total extractions: {results['total_extractions']}")

    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Corruption rate over time
    ax = axes[0, 0]
    ax.plot(results["model_data"]["Corruption_Rate"])
    ax.set_xlabel("Step")
    ax.set_ylabel("Corruption Rate")
    ax.set_title("Corruption Rate Over Time")
    ax.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label="50% threshold")
    ax.legend()

    # Mean integrity over time
    ax = axes[0, 1]
    ax.plot(results["model_data"]["Mean_Integrity"])
    ax.set_xlabel("Step")
    ax.set_ylabel("Mean Integrity")
    ax.set_title("Mean Integrity Over Time")

    # Total extractions over time
    ax = axes[1, 0]
    ax.plot(results["model_data"]["Total_Extractions"])
    ax.set_xlabel("Step")
    ax.set_ylabel("Cumulative Extractions")
    ax.set_title("Total Extraction Events")

    # Number of corrupted agents
    ax = axes[1, 1]
    ax.plot(results["model_data"]["Corrupted_Agents"])
    ax.set_xlabel("Step")
    ax.set_ylabel("Number Corrupted")
    ax.set_title("Corrupted Agents Over Time")

    plt.tight_layout()

    if args.output:
        plt.savefig(f"{args.output}/corruption_dynamics.png", dpi=150)
    else:
        plt.show()
