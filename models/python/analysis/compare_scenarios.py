"""
Compare Monte Carlo Scenario Results

Creates publication-quality comparison figures across pessimistic, baseline, and optimistic scenarios.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
from pathlib import Path


def load_scenario(csv_path: str, json_path: str, name: str) -> dict:
    """Load a single scenario's results."""
    df = pd.read_csv(csv_path)
    with open(json_path) as f:
        stats = json.load(f)
    return {
        'name': name,
        'df': df,
        'stats': stats['stats'],
        'params': stats['params']
    }


def plot_scenario_comparison(scenarios: list, output_path: str = None):
    """Create comprehensive scenario comparison figure."""
    fig = plt.figure(figsize=(16, 12))

    colors = {'Pessimistic': '#d62728', 'Baseline': '#1f77b4', 'Optimistic': '#2ca02c'}

    # 1. Time distribution comparison (overlaid histograms)
    ax1 = fig.add_subplot(2, 2, 1)
    for scenario in scenarios:
        name = scenario['name']
        df = scenario['df']
        extinction_df = df[df['reached_extinction'] == True]
        times = extinction_df['time_to_extinction']

        ax1.hist(times, bins=50, alpha=0.5, label=name, color=colors[name], density=True)
        ax1.axvline(scenario['stats']['median_time'], color=colors[name],
                   linestyle='--', linewidth=2)

    ax1.set_xlabel("Time to Extinction (years)", fontsize=12)
    ax1.set_ylabel("Density", fontsize=12)
    ax1.set_title("Time Distribution by Scenario", fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. CDF comparison
    ax2 = fig.add_subplot(2, 2, 2)
    for scenario in scenarios:
        name = scenario['name']
        df = scenario['df']
        extinction_df = df[df['reached_extinction'] == True]
        times = extinction_df['time_to_extinction'].sort_values()
        cdf = np.arange(1, len(times) + 1) / len(times)

        ax2.plot(times, cdf, linewidth=2, label=name, color=colors[name])

    ax2.axhline(0.5, color='gray', linestyle=':', alpha=0.5)
    ax2.set_xlabel("Time (years)", fontsize=12)
    ax2.set_ylabel("Cumulative Probability", fontsize=12)
    ax2.set_title("Cumulative Distribution: P(Extinction by Time T)", fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Box plot comparison
    ax3 = fig.add_subplot(2, 2, 3)
    box_data = []
    labels = []
    for scenario in scenarios:
        name = scenario['name']
        df = scenario['df']
        extinction_df = df[df['reached_extinction'] == True]
        box_data.append(extinction_df['time_to_extinction'].values)
        labels.append(name)

    bp = ax3.boxplot(box_data, labels=labels, patch_artist=True)
    for patch, name in zip(bp['boxes'], labels):
        patch.set_facecolor(colors[name])
        patch.set_alpha(0.7)

    ax3.set_ylabel("Time to Extinction (years)", fontsize=12)
    ax3.set_title("Time Distribution Box Plot", fontsize=14)
    ax3.grid(True, alpha=0.3, axis='y')

    # 4. Summary statistics table
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    # Build comparison table
    table_text = "Scenario Comparison Summary\n" + "=" * 50 + "\n\n"
    table_text += f"{'Metric':<25} {'Pessimistic':>12} {'Baseline':>12} {'Optimistic':>12}\n"
    table_text += "-" * 65 + "\n"

    metrics = [
        ('Extinction Rate', 'extinction_rate', lambda x: f"{x*100:.1f}%"),
        ('Median Time (yrs)', 'median_time', lambda x: f"{x:.0f}"),
        ('Mean Time (yrs)', 'mean_time', lambda x: f"{x:.0f}"),
        ('5th %ile (yrs)', 'p5_time', lambda x: f"{x:.0f}"),
        ('95th %ile (yrs)', 'p95_time', lambda x: f"{x:.0f}"),
        ('Mean Cycles', 'mean_cycles', lambda x: f"{x:.1f}"),
    ]

    for metric_name, key, fmt in metrics:
        values = [fmt(s['stats'][key]) for s in scenarios]
        table_text += f"{metric_name:<25} {values[0]:>12} {values[1]:>12} {values[2]:>12}\n"

    table_text += "\n" + "-" * 65 + "\n"
    table_text += "Parameters:\n"

    param_metrics = [
        ('Initial p_AI', 'p_ai', lambda x: f"{x:.0%}"),
        ('Cycle Duration', 'cycle_duration', lambda x: f"{x:.0f} yrs"),
        ('p_AI Growth Rate', 'p_ai_growth_rate', lambda x: f"{x:.0%}/cycle"),
    ]

    for metric_name, key, fmt in param_metrics:
        values = [fmt(s['params'][key]) for s in scenarios]
        table_text += f"{metric_name:<25} {values[0]:>12} {values[1]:>12} {values[2]:>12}\n"

    ax4.text(0.05, 0.95, table_text, transform=ax4.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

    plt.suptitle("Coordination Trilemma: Monte Carlo Scenario Analysis",
                 fontsize=16, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_timeline_ranges(scenarios: list, output_path: str = None):
    """Create a timeline visualization showing probability ranges."""
    fig, ax = plt.subplots(figsize=(14, 6))

    colors = {'Pessimistic': '#d62728', 'Baseline': '#1f77b4', 'Optimistic': '#2ca02c'}

    y_positions = [2, 1, 0]

    for i, scenario in enumerate(scenarios):
        name = scenario['name']
        s = scenario['stats']
        y = y_positions[i]

        # Plot range bar (5th to 95th percentile)
        ax.barh(y, s['p95_time'] - s['p5_time'], left=s['p5_time'],
               height=0.6, color=colors[name], alpha=0.3,
               label=f"{name} (90% CI)")

        # Plot IQR (25th to 75th percentile)
        ax.barh(y, s['p75_time'] - s['p25_time'], left=s['p25_time'],
               height=0.6, color=colors[name], alpha=0.6)

        # Plot median line
        ax.plot([s['median_time'], s['median_time']], [y - 0.3, y + 0.3],
               color='white', linewidth=3)
        ax.plot([s['median_time'], s['median_time']], [y - 0.3, y + 0.3],
               color=colors[name], linewidth=2)

        # Annotate
        ax.text(s['p95_time'] + 20, y,
               f"Median: {s['median_time']:.0f} yrs\n"
               f"90% CI: [{s['p5_time']:.0f}, {s['p95_time']:.0f}]",
               va='center', fontsize=9)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([s['name'] for s in scenarios])
    ax.set_xlabel("Time to Extinction/Enslavement (years)", fontsize=12)
    ax.set_title("Timeline Projections by Scenario", fontsize=14)
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim(0, max(s['stats']['p95_time'] for s in scenarios) * 1.3)

    # Add vertical lines for reference
    for year in [100, 500, 1000, 1500, 2000]:
        if year < ax.get_xlim()[1]:
            ax.axvline(year, color='gray', linestyle=':', alpha=0.3)
            ax.text(year, 2.5, f"{year}", ha='center', fontsize=8, color='gray')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare Monte Carlo scenarios")
    parser.add_argument("--data-dir", type=str, default=".", help="Directory with scenario results")
    parser.add_argument("--output", type=str, default=".", help="Output directory")

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all scenarios
    print("Loading scenario results...")
    scenarios = [
        load_scenario(
            data_dir / "montecarlo_pessimistic.csv",
            data_dir / "montecarlo_pessimistic.json",
            "Pessimistic"
        ),
        load_scenario(
            data_dir / "montecarlo_results.csv",
            data_dir / "montecarlo_stats.json",
            "Baseline"
        ),
        load_scenario(
            data_dir / "montecarlo_optimistic.csv",
            data_dir / "montecarlo_optimistic.json",
            "Optimistic"
        ),
    ]

    print("Generating scenario comparison...")
    plot_scenario_comparison(scenarios, output_dir / "scenario_comparison.png")

    print("Generating timeline ranges...")
    plot_timeline_ranges(scenarios, output_dir / "timeline_ranges.png")

    print(f"Figures saved to {output_dir}/")
