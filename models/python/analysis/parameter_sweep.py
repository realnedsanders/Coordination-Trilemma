"""
Parameter Sweep for Corruption Dynamics Model

Performs sensitivity analysis to identify which parameters are
load-bearing for the corruption inevitability result.
"""

import numpy as np
import pandas as pd
from itertools import product
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ProcessPoolExecutor
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abm.corruption_dynamics import run_experiment


def single_run(params: dict) -> dict:
    """Run a single experiment and return results."""
    # Remove internal tracking keys before passing to model
    run_params = {k: v for k, v in params.items() if not k.startswith("_")}
    results = run_experiment(**run_params)
    return {
        "final_corruption_rate": results["final_corruption_rate"],
        "final_mean_integrity": results["final_mean_integrity"],
        "total_extractions": results["total_extractions"],
        **{k: v for k, v in params.items() if k != "n_steps" and not k.startswith("_")}
    }


def parameter_sweep(
    param_ranges: dict,
    fixed_params: dict = None,
    n_replications: int = 10,
    n_steps: int = 200,
    n_workers: int = 4
) -> pd.DataFrame:
    """
    Perform parameter sweep over specified ranges.

    Args:
        param_ranges: Dict mapping parameter names to lists of values
        fixed_params: Dict of parameters to hold constant
        n_replications: Number of replications per parameter combination
        n_steps: Number of model steps
        n_workers: Number of parallel workers

    Returns:
        DataFrame with results for all parameter combinations
    """
    if fixed_params is None:
        fixed_params = {}

    # Generate all parameter combinations
    param_names = list(param_ranges.keys())
    param_values = list(param_ranges.values())
    combinations = list(product(*param_values))

    # Create list of all runs (combinations x replications)
    all_runs = []
    for combo in combinations:
        params = dict(zip(param_names, combo))
        params.update(fixed_params)
        params["n_steps"] = n_steps

        for rep in range(n_replications):
            run_params = params.copy()
            run_params["seed"] = rep  # Different seed per replication
            run_params["_replication"] = rep
            all_runs.append(run_params)

    # Run all experiments
    results = []
    print(f"Running {len(all_runs)} experiments...")

    if n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            for result in tqdm(executor.map(single_run, all_runs), total=len(all_runs)):
                results.append(result)
    else:
        for params in tqdm(all_runs):
            results.append(single_run(params))

    return pd.DataFrame(results)


def analyze_sensitivity(results_df: pd.DataFrame, param_name: str) -> dict:
    """
    Analyze sensitivity of corruption rate to a parameter.

    Returns:
        Dict with sensitivity statistics
    """
    grouped = results_df.groupby(param_name)["final_corruption_rate"]

    return {
        "param": param_name,
        "mean_by_value": grouped.mean().to_dict(),
        "std_by_value": grouped.std().to_dict(),
        "range": grouped.mean().max() - grouped.mean().min(),
        "correlation": results_df[[param_name, "final_corruption_rate"]].corr().iloc[0, 1]
    }


def plot_sensitivity(results_df: pd.DataFrame, param_name: str, output_path: str = None):
    """Plot corruption rate vs parameter value."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Calculate mean and confidence interval
    grouped = results_df.groupby(param_name)["final_corruption_rate"]
    means = grouped.mean()
    stds = grouped.std()

    ax.errorbar(means.index, means.values, yerr=1.96*stds.values,
                marker='o', capsize=5, capthick=2)

    ax.set_xlabel(param_name, fontsize=12)
    ax.set_ylabel("Final Corruption Rate", fontsize=12)
    ax.set_title(f"Sensitivity: Corruption Rate vs {param_name}", fontsize=14)
    ax.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label="50% threshold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


def plot_heatmap(results_df: pd.DataFrame, param1: str, param2: str, output_path: str = None):
    """Plot heatmap of corruption rate for two parameters."""
    pivot = results_df.pivot_table(
        values="final_corruption_rate",
        index=param1,
        columns=param2,
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn_r", ax=ax,
                vmin=0, vmax=1)

    ax.set_title(f"Corruption Rate: {param1} vs {param2}", fontsize=14)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parameter sweep for corruption model")
    parser.add_argument("--output", type=str, default="../../figures/static",
                        help="Output directory for figures")
    parser.add_argument("--workers", type=int, default=4, help="Number of workers")
    parser.add_argument("--reps", type=int, default=10, help="Replications per combo")

    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Define parameter ranges for sweep
    param_ranges = {
        "integrity_mean": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        "base_detection_prob": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    }

    fixed_params = {
        "n_enforcers": 100,
        "oversight_structure": "hierarchical",
        "integrity_decay": True,
        "corruption_contagion": True,
    }

    # Run sweep
    results = parameter_sweep(
        param_ranges,
        fixed_params=fixed_params,
        n_replications=args.reps,
        n_workers=args.workers
    )

    # Save results
    results.to_csv(f"{args.output}/parameter_sweep_results.csv", index=False)

    # Analyze sensitivity
    print("\nSensitivity Analysis:")
    for param in param_ranges.keys():
        sens = analyze_sensitivity(results, param)
        print(f"\n{param}:")
        print(f"  Range of effect: {sens['range']:.3f}")
        print(f"  Correlation: {sens['correlation']:.3f}")

        # Plot individual sensitivity
        plot_sensitivity(results, param, f"{args.output}/sensitivity_{param}.png")

    # Plot heatmap
    plot_heatmap(
        results,
        "integrity_mean",
        "base_detection_prob",
        f"{args.output}/heatmap_integrity_detection.png"
    )

    print(f"\nFigures saved to {args.output}/")
