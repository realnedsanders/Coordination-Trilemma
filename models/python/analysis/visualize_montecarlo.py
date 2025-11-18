"""
Visualize Monte Carlo Simulation Results

Creates publication-quality figures from the Go Monte Carlo output.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import argparse
from pathlib import Path


def load_results(csv_path: str, json_path: str = None) -> tuple:
    """Load simulation results from CSV and optional JSON stats."""
    df = pd.read_csv(csv_path)

    stats = None
    if json_path and Path(json_path).exists():
        with open(json_path) as f:
            stats = json.load(f)

    return df, stats


def plot_time_distribution(df: pd.DataFrame, stats: dict, output_path: str = None):
    """Plot distribution of time to extinction."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Filter to extinction cases
    extinction_df = df[df['reached_extinction'] == True]
    times = extinction_df['time_to_extinction']

    # Histogram
    ax = axes[0]
    ax.hist(times, bins=50, edgecolor='black', alpha=0.7, density=True)

    # Add statistics lines
    if stats:
        s = stats['stats']
        ax.axvline(s['mean_time'], color='r', linestyle='-', linewidth=2,
                   label=f"Mean: {s['mean_time']:.0f} yrs")
        ax.axvline(s['median_time'], color='g', linestyle='--', linewidth=2,
                   label=f"Median: {s['median_time']:.0f} yrs")
        ax.axvline(s['p5_time'], color='orange', linestyle=':', linewidth=2,
                   label=f"5th %ile: {s['p5_time']:.0f} yrs")
        ax.axvline(s['p95_time'], color='orange', linestyle=':', linewidth=2,
                   label=f"95th %ile: {s['p95_time']:.0f} yrs")

    ax.set_xlabel("Time to Extinction (years)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title("Distribution of Time to Extinction/Enslavement", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # CDF
    ax = axes[1]
    sorted_times = np.sort(times)
    cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
    ax.plot(sorted_times, cdf, linewidth=2)

    # Add reference lines
    ax.axhline(0.5, color='g', linestyle='--', alpha=0.5, label="50%")
    ax.axhline(0.95, color='orange', linestyle=':', alpha=0.5, label="95%")

    ax.set_xlabel("Time (years)", fontsize=12)
    ax.set_ylabel("Cumulative Probability", fontsize=12)
    ax.set_title("Cumulative Distribution: P(Extinction by Time T)", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


def plot_cycles_distribution(df: pd.DataFrame, stats: dict, output_path: str = None):
    """Plot distribution of cycles to extinction."""
    fig, ax = plt.subplots(figsize=(10, 6))

    extinction_df = df[df['reached_extinction'] == True]
    cycles = extinction_df['num_cycles']

    # Count by cycle number
    cycle_counts = cycles.value_counts().sort_index()

    ax.bar(cycle_counts.index, cycle_counts.values, edgecolor='black', alpha=0.7)

    if stats:
        s = stats['stats']
        ax.axvline(s['mean_cycles'], color='r', linestyle='-', linewidth=2,
                   label=f"Mean: {s['mean_cycles']:.1f}")
        ax.axvline(s['median_cycles'], color='g', linestyle='--', linewidth=2,
                   label=f"Median: {s['median_cycles']:.0f}")

    ax.set_xlabel("Number of Cycles", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Distribution of Cycles to Extinction", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


def plot_scenario_comparison(output_path: str = None):
    """
    Plot comparison of different scenarios (baseline, optimistic, pessimistic).

    This requires running simulations with different parameters first.
    """
    # Define scenarios
    scenarios = {
        'Pessimistic': {'p_ai': 0.10, 'growth': 0.15, 'cycle': 30},
        'Baseline': {'p_ai': 0.05, 'growth': 0.10, 'cycle': 50},
        'Optimistic': {'p_ai': 0.02, 'growth': 0.05, 'cycle': 75},
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {'Pessimistic': 'red', 'Baseline': 'blue', 'Optimistic': 'green'}

    # This is a placeholder - in real use, we'd load actual simulation results
    # For now, show theoretical distributions based on geometric series

    for name, params in scenarios.items():
        # Theoretical expected cycles: 1/p_ai initially
        # But p_ai grows, so effective is less

        # Simple approximation: E[cycles] ≈ ln(p_ai_max/p_ai) / ln(1+growth)
        expected_cycles = np.log(0.99 / params['p_ai']) / np.log(1 + params['growth'])
        expected_time = expected_cycles * params['cycle']

        # Plot as vertical line with annotation
        ax.axvline(expected_time, color=colors[name], linewidth=2,
                   label=f"{name}: ~{expected_time:.0f} yrs")

    ax.set_xlabel("Time to Extinction (years)", fontsize=12)
    ax.set_xlim(0, 500)
    ax.set_title("Scenario Comparison: Expected Time to Extinction", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add annotation
    ax.text(0.95, 0.95,
            "Based on:\n" +
            "• p_ai growth rates\n" +
            "• Cycle durations\n" +
            "• Initial AI adoption prob.",
            transform=ax.transAxes, fontsize=9,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


def plot_summary_dashboard(df: pd.DataFrame, stats: dict, output_path: str = None):
    """Create a summary dashboard with multiple plots."""
    fig = plt.figure(figsize=(16, 10))

    # Time distribution
    ax1 = fig.add_subplot(2, 2, 1)
    extinction_df = df[df['reached_extinction'] == True]
    times = extinction_df['time_to_extinction']
    ax1.hist(times, bins=40, edgecolor='black', alpha=0.7)
    if stats:
        ax1.axvline(stats['stats']['median_time'], color='r', linestyle='--',
                    label=f"Median: {stats['stats']['median_time']:.0f} yrs")
    ax1.set_xlabel("Years")
    ax1.set_ylabel("Count")
    ax1.set_title("Time to Extinction Distribution")
    ax1.legend()

    # Cycles distribution
    ax2 = fig.add_subplot(2, 2, 2)
    cycles = extinction_df['num_cycles']
    ax2.hist(cycles, bins=range(1, int(cycles.max()) + 2), edgecolor='black', alpha=0.7)
    ax2.set_xlabel("Cycles")
    ax2.set_ylabel("Count")
    ax2.set_title("Cycles to Extinction Distribution")

    # Final p_ai distribution
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.hist(extinction_df['final_p_ai'], bins=30, edgecolor='black', alpha=0.7)
    ax3.set_xlabel("Final p_AI")
    ax3.set_ylabel("Count")
    ax3.set_title("Final AI Adoption Probability at Extinction")

    # Summary statistics text
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    if stats:
        s = stats['stats']
        p = stats['params']
        text = f"""
Monte Carlo Simulation Results
==============================

Simulations: {s['n']:,}
Extinction Rate: {s['extinction_rate']*100:.1f}%

Time to Extinction:
  Mean: {s['mean_time']:.0f} years (σ={s['std_time']:.0f})
  Median: {s['median_time']:.0f} years
  90% CI: [{s['p5_time']:.0f}, {s['p95_time']:.0f}] years

Cycles to Extinction:
  Mean: {s['mean_cycles']:.1f}
  Median: {s['median_cycles']:.0f}

Parameters:
  Initial p_AI: {p['p_ai']}
  Cycle duration: {p['cycle_duration']:.0f} ± {p['cycle_duration_std']:.0f} years
  p_AI growth rate: {p['p_ai_growth_rate']*100:.0f}% per cycle
"""
        ax4.text(0.1, 0.9, text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    plt.suptitle("Coordination Trilemma: Default Trajectory Monte Carlo Analysis",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize Monte Carlo results")
    parser.add_argument("--csv", type=str, required=True, help="Path to results CSV")
    parser.add_argument("--json", type=str, help="Path to stats JSON")
    parser.add_argument("--output", type=str, default=".", help="Output directory")

    args = parser.parse_args()

    print(f"Loading results from {args.csv}...")
    df, stats = load_results(args.csv, args.json)

    print(f"Loaded {len(df)} simulations")

    # Generate all plots
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating time distribution plot...")
    plot_time_distribution(df, stats, output_dir / "montecarlo_time_dist.png")

    print("Generating cycles distribution plot...")
    plot_cycles_distribution(df, stats, output_dir / "montecarlo_cycles_dist.png")

    print("Generating summary dashboard...")
    plot_summary_dashboard(df, stats, output_dir / "montecarlo_dashboard.png")

    print(f"Figures saved to {output_dir}/")
