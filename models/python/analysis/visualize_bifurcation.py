"""
Visualize Bifurcation Analysis Results

Generates the bifurcation diagram figure from JSON output
(typically from the fast Go implementation).

This allows the pipeline:
  Go (fast simulation) -> JSON -> Python (visualization) -> PNG
"""

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_results(json_path: str) -> dict:
    """Load bifurcation results from JSON file."""
    with open(json_path) as f:
        return json.load(f)


def plot_bifurcation(results: dict, output_path: str = None):
    """
    Generate bifurcation diagram from results.

    Args:
        results: Dictionary with 'results' list and 'theta_crit'
        output_path: Path to save figure (if None, displays)
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Extract data
    initial_rates = [r["initial_rate"] for r in results["results"]]
    final_rates = [r["final_rate"] for r in results["results"]]
    theta_crit = results["theta_crit"]

    # Plot scatter of all runs
    ax.scatter(initial_rates, final_rates, alpha=0.5, s=20)

    # Reference line (no change)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label="No change")

    # Mark critical threshold
    ax.axvline(x=theta_crit, color='r', linestyle='--',
               label=f"$\\theta_{{crit}}$ = {theta_crit:.2f}")
    ax.axhline(y=theta_crit, color='r', linestyle='--', alpha=0.5)

    ax.set_xlabel("Initial Cooperation Rate", fontsize=12)
    ax.set_ylabel("Final Cooperation Rate", fontsize=12)
    ax.set_title("Bifurcation Analysis: Critical Mass Threshold", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Figure saved to {output_path}")
    else:
        plt.show()

    plt.close()


def compute_statistics(results: dict) -> dict:
    """Compute summary statistics from bifurcation results."""
    theta_crit = results["theta_crit"]

    # Group by initial rate
    by_rate = {}
    for r in results["results"]:
        rate = r["initial_rate"]
        if rate not in by_rate:
            by_rate[rate] = []
        by_rate[rate].append(r["final_rate"])

    # Compute stats
    stats = {
        "theta_crit": theta_crit,
        "n_rates": len(by_rate),
        "n_reps": len(results["results"]) // len(by_rate) if by_rate else 0,
        "rates": {}
    }

    for rate, finals in sorted(by_rate.items()):
        mean_final = np.mean(finals)
        std_final = np.std(finals)

        # Classify outcome
        if mean_final > 0.8:
            outcome = "cooperation"
        elif mean_final < 0.2:
            outcome = "defection"
        else:
            outcome = "mixed"

        stats["rates"][rate] = {
            "mean": mean_final,
            "std": std_final,
            "outcome": outcome
        }

    # Find empirical threshold (where outcome switches)
    sorted_rates = sorted(stats["rates"].keys())
    empirical_threshold = None
    for i in range(len(sorted_rates) - 1):
        r1, r2 = sorted_rates[i], sorted_rates[i+1]
        o1, o2 = stats["rates"][r1]["outcome"], stats["rates"][r2]["outcome"]
        if o1 == "defection" and o2 in ["mixed", "cooperation"]:
            empirical_threshold = (r1 + r2) / 2
            break

    stats["empirical_threshold"] = empirical_threshold

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Visualize bifurcation analysis results from JSON"
    )
    parser.add_argument(
        "--json", "-j",
        type=str,
        required=True,
        help="Path to JSON results file"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for figure"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print summary statistics"
    )

    args = parser.parse_args()

    # Load results
    results = load_results(args.json)

    # Print stats if requested
    if args.stats:
        stats = compute_statistics(results)
        print(f"\nBifurcation Analysis Statistics:")
        print(f"  Theoretical θ_crit: {stats['theta_crit']:.3f}")
        if stats['empirical_threshold']:
            print(f"  Empirical threshold: {stats['empirical_threshold']:.3f}")
        print(f"  Rates tested: {stats['n_rates']}")
        print(f"  Replications: {stats['n_reps']}")
        print()

    # Generate figure
    if args.output:
        output_path = Path(args.output) / "bifurcation_analysis.png"
    else:
        output_path = None

    plot_bifurcation(results, output_path)

    print(f"Critical threshold θ_crit = {results['theta_crit']:.3f}")


if __name__ == "__main__":
    main()
