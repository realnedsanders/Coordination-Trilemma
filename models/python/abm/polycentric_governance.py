"""
Polycentric Governance Model (Ostrom's Design Principles)

DEPRECATION NOTICE: This Python implementation has been superseded by the Go
implementation in models/go/ostrom/ which properly implements scale-dependent
degradation effects. Use `make go-ostrom` or `make ostrom-scale` for production
simulations. This file is retained for reference and basic testing only.

This model tests whether Ostrom's design principles for successful commons
governance can break the corruption inevitability demonstrated in the
hierarchical enforcement model.

Key differences from hierarchical model:
1. Peer monitoring (not hierarchical) - detection doesn't decrease with corruption
2. Graduated sanctions - agents can recover from corrupt state
3. Collective-choice - agents have stake in rule-making
4. Nested enterprises - multiple overlapping groups

Ostrom's 8 Design Principles:
1. Clearly defined boundaries
2. Congruence between rules and local conditions
3. Collective-choice arrangements
4. Monitoring (by appropriators)
5. Graduated sanctions
6. Conflict-resolution mechanisms
7. Minimal recognition of rights to organize
8. Nested enterprises
"""

import numpy as np
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from typing import Optional
import yaml


class Participant(Agent):
    """
    A participant in a polycentric governance system.

    Unlike hierarchical enforcers, participants:
    - Monitor each other (peer monitoring)
    - Can recover from corruption (graduated sanctions)
    - Have stake in collective outcomes
    """

    def __init__(
        self,
        model: "PolycentricModel",
        integrity: float,
        group_id: int
    ):
        super().__init__(model)
        self.integrity = integrity
        self.base_integrity = integrity
        self.corrupt = False
        self.group_id = group_id
        self.sanctions_received = 0

    def step(self):
        """Decide whether to be corrupt or honest."""
        if self.corrupt:
            self._consider_reform()
        else:
            self._consider_corruption()

        # Integrity dynamics
        self._update_integrity()

    def _consider_corruption(self):
        """
        Decide whether to become corrupt.

        Key difference from hierarchical model:
        - Detection probability is based on peer monitoring
        - Doesn't decrease as others corrupt (maybe increases)
        """
        # Potential gain from corruption
        corruption_gain = self.model.corruption_gain

        # Detection probability under peer monitoring
        # In Ostrom systems, monitoring is by participants themselves
        # More corruption can actually INCREASE vigilance (unlike hierarchy)
        group_corruption = self._get_group_corruption_rate()

        if self.model.ostrom_monitoring:
            # Peer monitoring: detection stays high or increases with corruption
            # (participants are vigilant when they see others cheating)
            base_detection = self.model.base_detection_prob
            vigilance_boost = self.model.vigilance_factor * group_corruption
            detection_prob = min(0.95, base_detection + vigilance_boost)
        else:
            # Hierarchical monitoring: detection decreases with corruption
            detection_prob = self.model.base_detection_prob * (1 - group_corruption)

        # Expected cost if detected
        if self.model.graduated_sanctions:
            # Graduated sanctions: proportional to offense, allows recovery
            expected_penalty = self.model.sanction_base * (1 + self.sanctions_received)
        else:
            # Binary sanctions: severe, no recovery path
            expected_penalty = self.model.sanction_base * 5

        # Cost from integrity loss
        integrity_cost = self.integrity * self.model.integrity_weight

        # Collective-choice effect: stake in system
        if self.model.collective_choice:
            # Participants who helped make rules are more likely to follow them
            stake_cost = self.model.stake_factor * (1 - group_corruption)
        else:
            stake_cost = 0

        # Decision
        expected_benefit = corruption_gain
        expected_cost = detection_prob * expected_penalty + integrity_cost + stake_cost

        # Corrupt if benefit exceeds cost (with some noise)
        noise = np.random.normal(0, 0.1)
        if expected_benefit + noise > expected_cost:
            self.corrupt = True

    def _consider_reform(self):
        """
        Consider returning to honest behavior.

        Only possible with graduated sanctions (Ostrom principle 5).
        """
        if not self.model.graduated_sanctions:
            return  # No path to recovery

        # Reform incentives
        group_cooperation = 1 - self._get_group_corruption_rate()

        # Social pressure from honest peers
        social_pressure = self.model.social_pressure_factor * group_cooperation

        # Diminishing returns to continued corruption
        continued_gain = self.model.corruption_gain * (0.9 ** self.sanctions_received)

        # Recovery of integrity over time
        integrity_recovery = self.base_integrity * 0.1

        # Decision to reform
        reform_benefit = social_pressure + integrity_recovery
        reform_cost = continued_gain

        if reform_benefit > reform_cost + np.random.normal(0, 0.1):
            self.corrupt = False
            self.sanctions_received = max(0, self.sanctions_received - 1)

    def _get_group_corruption_rate(self) -> float:
        """Get corruption rate in agent's group."""
        group_members = [a for a in self.model.agents if a.group_id == self.group_id]
        if not group_members:
            return 0.0
        return sum(1 for a in group_members if a.corrupt) / len(group_members)

    def _update_integrity(self):
        """Update integrity based on behavior and environment."""
        if self.corrupt:
            # Integrity decays when corrupt
            self.integrity *= (1 - self.model.integrity_decay_rate)
            self.sanctions_received += 1
        else:
            # Integrity can recover when honest (key Ostrom difference)
            if self.model.graduated_sanctions:
                recovery = (self.base_integrity - self.integrity) * self.model.integrity_recovery_rate
                self.integrity = min(self.base_integrity, self.integrity + recovery)


class PolycentricModel(Model):
    """
    Model of polycentric governance with Ostrom's design principles.

    Tests whether these principles can overcome corruption inevitability.

    Ostrom parameters:
        ostrom_monitoring: Peer monitoring instead of hierarchical
        graduated_sanctions: Recovery path from corruption
        collective_choice: Stake in rule-making
        n_groups: Number of nested groups (polycentric structure)

    Standard parameters:
        n_participants: Number of participants
        corruption_gain: Benefit from corruption
        base_detection_prob: Base probability of detection
        integrity_mean/std: Distribution of initial integrity
        seed: Random seed
    """

    def __init__(
        self,
        n_participants: int = 100,
        n_groups: int = 5,
        # Ostrom principles
        ostrom_monitoring: bool = True,
        graduated_sanctions: bool = True,
        collective_choice: bool = True,
        # Monitoring parameters
        base_detection_prob: float = 0.2,
        vigilance_factor: float = 0.4,
        # Sanction parameters
        sanction_base: float = 0.5,
        social_pressure_factor: float = 0.3,
        # Stakes and incentives
        corruption_gain: float = 2.0,
        stake_factor: float = 0.2,
        integrity_weight: float = 0.1,
        # Integrity dynamics
        integrity_mean: float = 5.0,
        integrity_std: float = 1.0,
        integrity_decay_rate: float = 0.05,
        integrity_recovery_rate: float = 0.1,
        seed: Optional[int] = None
    ):
        super().__init__(seed=seed)

        if seed is not None:
            np.random.seed(seed)

        # Store parameters
        self.n_participants = n_participants
        self.n_groups = n_groups
        self.ostrom_monitoring = ostrom_monitoring
        self.graduated_sanctions = graduated_sanctions
        self.collective_choice = collective_choice
        self.base_detection_prob = base_detection_prob
        self.vigilance_factor = vigilance_factor
        self.sanction_base = sanction_base
        self.social_pressure_factor = social_pressure_factor
        self.corruption_gain = corruption_gain
        self.stake_factor = stake_factor
        self.integrity_weight = integrity_weight
        self.integrity_decay_rate = integrity_decay_rate
        self.integrity_recovery_rate = integrity_recovery_rate

        # Create participants in groups
        for i in range(n_participants):
            integrity = max(0.1, np.random.normal(integrity_mean, integrity_std))
            group_id = i % n_groups  # Distribute across groups
            Participant(self, integrity, group_id)

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Corruption_Rate": lambda m: sum(1 for a in m.agents if a.corrupt) / len(m.agents),
                "Mean_Integrity": lambda m: np.mean([a.integrity for a in m.agents]),
                "Reform_Rate": lambda m: self._reform_rate(),
            },
            agent_reporters={
                "Corrupt": "corrupt",
                "Integrity": "integrity",
                "Group": "group_id",
                "Sanctions": "sanctions_received",
            }
        )

    def _reform_rate(self) -> float:
        """Placeholder for tracking reforms - would need history."""
        return 0.0  # TODO: track actual reforms

    def step(self):
        """Advance model by one step."""
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

    def run(self, steps: int = 200) -> None:
        """Run model for specified steps."""
        for _ in range(steps):
            self.step()


def run_experiment(
    config_path: str = None,
    n_steps: int = 200,
    **kwargs
) -> dict:
    """
    Run a polycentric governance experiment.

    Returns dictionary with results.
    """
    if config_path:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        config.update(kwargs)
    else:
        config = kwargs

    model = PolycentricModel(**config)
    model.run(n_steps)

    model_data = model.datacollector.get_model_vars_dataframe()

    return {
        "model_data": model_data,
        "final_corruption_rate": sum(1 for a in model.agents if a.corrupt) / len(model.agents),
        "final_mean_integrity": np.mean([a.integrity for a in model.agents]),
        "config": config,
    }


def compare_governance_systems(
    n_replications: int = 10,
    n_steps: int = 200,
    **common_params
) -> dict:
    """
    Compare hierarchical vs polycentric governance outcomes.

    Returns results for:
    1. Hierarchical (no Ostrom principles)
    2. Partial Ostrom (some principles)
    3. Full Ostrom (all principles)
    """
    results = {
        'hierarchical': [],
        'partial_ostrom': [],
        'full_ostrom': []
    }

    for rep in range(n_replications):
        # Hierarchical (baseline - like original corruption model)
        hierarchical = run_experiment(
            ostrom_monitoring=False,
            graduated_sanctions=False,
            collective_choice=False,
            n_groups=1,  # Single hierarchy
            seed=rep,
            n_steps=n_steps,
            **common_params
        )
        results['hierarchical'].append(hierarchical['final_corruption_rate'])

        # Partial Ostrom (just peer monitoring)
        partial = run_experiment(
            ostrom_monitoring=True,
            graduated_sanctions=False,
            collective_choice=False,
            n_groups=5,
            seed=rep,
            n_steps=n_steps,
            **common_params
        )
        results['partial_ostrom'].append(partial['final_corruption_rate'])

        # Full Ostrom (all principles)
        full = run_experiment(
            ostrom_monitoring=True,
            graduated_sanctions=True,
            collective_choice=True,
            n_groups=5,
            seed=rep,
            n_steps=n_steps,
            **common_params
        )
        results['full_ostrom'].append(full['final_corruption_rate'])

    return {
        'hierarchical': {
            'mean': np.mean(results['hierarchical']),
            'std': np.std(results['hierarchical']),
            'values': results['hierarchical']
        },
        'partial_ostrom': {
            'mean': np.mean(results['partial_ostrom']),
            'std': np.std(results['partial_ostrom']),
            'values': results['partial_ostrom']
        },
        'full_ostrom': {
            'mean': np.mean(results['full_ostrom']),
            'std': np.std(results['full_ostrom']),
            'values': results['full_ostrom']
        }
    }


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser(description="Run polycentric governance model")
    parser.add_argument("--steps", type=int, default=200, help="Number of steps")
    parser.add_argument("--participants", type=int, default=100, help="Number of participants")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--compare", action="store_true", help="Compare governance systems")

    args = parser.parse_args()

    if args.compare:
        print("Comparing governance systems...")
        comparison = compare_governance_systems(
            n_replications=10,
            n_steps=args.steps,
            n_participants=args.participants
        )

        print("\n=== Governance System Comparison ===\n")
        for system, stats in comparison.items():
            print(f"{system}:")
            print(f"  Mean corruption rate: {stats['mean']:.2%}")
            print(f"  Std deviation: {stats['std']:.2%}")
            print()

        # Plot comparison
        fig, ax = plt.subplots(figsize=(10, 6))

        systems = list(comparison.keys())
        means = [comparison[s]['mean'] for s in systems]
        stds = [comparison[s]['std'] for s in systems]

        x = range(len(systems))
        bars = ax.bar(x, means, yerr=stds, capsize=5, alpha=0.7, edgecolor='black')

        # Color code
        colors = ['#d62728', '#ff7f0e', '#2ca02c']
        for bar, color in zip(bars, colors):
            bar.set_facecolor(color)

        ax.set_xticks(x)
        ax.set_xticklabels(['Hierarchical\n(No Ostrom)', 'Partial Ostrom\n(Peer Monitoring)', 'Full Ostrom\n(All Principles)'])
        ax.set_ylabel("Final Corruption Rate", fontsize=12)
        ax.set_title("Corruption Outcomes by Governance System", fontsize=14)
        ax.set_ylim(0, 1.1)
        ax.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for i, (mean, std) in enumerate(zip(means, stds)):
            ax.text(i, mean + std + 0.05, f"{mean:.0%}", ha='center', fontsize=10)

        plt.tight_layout()

        if args.output:
            plt.savefig(f"{args.output}/governance_comparison.png", dpi=150)
            print(f"Figure saved to {args.output}/governance_comparison.png")
        else:
            plt.show()

    else:
        # Single run with full Ostrom
        print("Running polycentric governance model...")
        results = run_experiment(
            n_participants=args.participants,
            n_steps=args.steps,
            seed=args.seed,
            ostrom_monitoring=True,
            graduated_sanctions=True,
            collective_choice=True
        )

        print(f"\nFinal corruption rate: {results['final_corruption_rate']:.2%}")
        print(f"Final mean integrity: {results['final_mean_integrity']:.2f}")

        # Plot time series
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        ax = axes[0]
        ax.plot(results['model_data']['Corruption_Rate'])
        ax.set_xlabel("Step")
        ax.set_ylabel("Corruption Rate")
        ax.set_title("Corruption Rate Over Time (Polycentric)")
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        ax.plot(results['model_data']['Mean_Integrity'])
        ax.set_xlabel("Step")
        ax.set_ylabel("Mean Integrity")
        ax.set_title("Mean Integrity Over Time")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if args.output:
            plt.savefig(f"{args.output}/polycentric_dynamics.png", dpi=150)
        else:
            plt.show()
