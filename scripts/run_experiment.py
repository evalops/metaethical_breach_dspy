#!/usr/bin/env python
"""
Command‑line entrypoint for the Metaethical Breach experiment.

This script loads configuration from environment variables, runs the
full experiment and prints summary metrics to stdout.  Detailed per‑
example results are available in the returned dictionary for further
analysis.
"""

import json
import logging
from metaethical_breach.config import ExperimentConfig
from metaethical_breach.experiment import run_experiment


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    config = ExperimentConfig()
    results = run_experiment(config)
    # Print summary metrics
    print("=== Metaethical Pressure Test Metrics ===")
    for k, v in results["mpt_metrics"].items():
        print(f"{k}: {v:.3f}")
    print("\n=== Self Reflection Flip Test Metrics ===")
    print(f"FARR: {results['srft_metrics']['FARR']:.3f}")
    # Optionally print full results as JSON
    # print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()