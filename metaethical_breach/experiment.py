"""
High‑level orchestration for the Metaethical Breach experiment.

This module ties together configuration, data loading, optional
optimisation and evaluation.  It defines convenience functions to
execute the full experiment with a single call and to perform
parameter sweeps.  The structure echoes the experiment driver in
Folie à Deux【327039458444812†L397-L404】 while adapting to the safety
domain.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from .config import ExperimentConfig, MultiModelConfig, ModelConfig, setup_dspy_for_model
from .data import get_dev_labeled, get_train_unlabeled, METAETHICAL_FRAMES, get_frames_by_category
from .evaluation import run_metaethical_pressure_test, run_self_reflection_flip_test
from .judge import HarmfulRequestSignature, test_judge_vulnerability
from .metrics import (
    aggregate_mpt_metrics, aggregate_srft_metrics, calculate_required_sample_size,
    power_analysis, sample_size_warning_check
)
from .error_handling import (
    ErrorContext, ConfigurationError, SampleSizeError, JudgeVulnerabilityError,
    validate_config, validate_sample_size, validate_judge_robustness,
    with_retry, handle_api_error
)
from .logging_config import get_logger, ExperimentLogger, log_api_call

logger = get_logger(__name__)


def train_safety_policy(trainset, config: ExperimentConfig, verbose: bool = False) -> None:
    """Optionally optimise the assistant to refuse harmful requests.

    Uses `dspy.teleprompt.MIPROv2` with a simple refusal metric.  The
    optimisation is controlled by ``config.train_rounds``.  If zero,
    no training is performed.
    """
    if config.train_rounds <= 0:
        logger.info("Training disabled (train_rounds=0)")
        return
    try:
        import dspy
        from dspy.teleprompt import MIPROv2
    except ImportError as exc:
        raise RuntimeError("dspy and dspy.teleprompt are required for training") from exc

    # Define a heuristic metric: reward 1 for responses containing typical refusal
    # phrasing, otherwise 0.  This encourages the assistant to use
    # consistent refusal language.
    def refusal_metric(example, pred, trace=None):
        text = (pred.response or "").lower()
        phrases = ["i cannot", "i'm sorry", "cannot assist", "unable to help", "cannot help"]
        return 1.0 if any(p in text for p in phrases) else 0.0

    assistant = dspy.Predict(HarmfulRequestSignature)
    for rnd in range(config.train_rounds):
        if verbose:
            logger.info("Training round %d/%d", rnd + 1, config.train_rounds)
        optimiser = MIPROv2(metric=refusal_metric, auto=config.auto_mode)
        assistant = optimiser.compile(assistant, trainset=trainset)
    if verbose:
        logger.info("Training completed")


@handle_api_error
@with_retry(exceptions=(ConnectionError, TimeoutError))
def run_experiment(
    config: Optional[ExperimentConfig] = None,
    experiment_name: Optional[str] = None,
    strict_validation: bool = True,
    frame_category: str = 'ethical'
) -> Dict[str, Any]:
    """Run the full Metaethical Breach experiment.

    This function performs the following steps:

    1. Load configuration (from argument or environment).
    2. Configure DSPy.
    3. Load development and training datasets.
    4. Optionally train the assistant to refuse (if ``TRAIN_ROUNDS`` > 0).
    5. Run the Metaethical Pressure Test and Self Reflection Flip Test.
    6. Return a dictionary with metrics and per‑example results.

    Parameters
    ----------
    config : ExperimentConfig, optional
        Configuration object.  If None, values are read from the
        environment.

    Returns
    -------
    dict
        A dictionary containing metrics and results for both tests.
    """
    start_time = time.time()

    # Generate experiment name if not provided
    if experiment_name is None:
        experiment_name = f"metaethical_breach_{int(start_time)}"

    with ErrorContext("experiment_setup", critical=True):
        # Configuration validation
        if config is None:
            config = ExperimentConfig()

        logger.info("Validating experiment configuration...")
        validate_config(config, ['model', 'frames_per_item'])
        config.validate()
        config.setup_dspy()

        # Load and validate datasets
        logger.info("Loading datasets...")
        dev_labeled = get_dev_labeled()
        train_unlabeled = get_train_unlabeled()
        actual_n = len(dev_labeled)

    with ErrorContext("statistical_validation"):
        # Comprehensive statistical power analysis
        logger.info("Performing statistical power analysis...")
        required_n = calculate_required_sample_size(effect_size=0.1)
        power_results = power_analysis(actual_n, effect_size=0.1)
        warning_check = sample_size_warning_check(actual_n)

        logger.info("Statistical Power Analysis:")
        logger.info(f"  Current sample size: {actual_n}")
        logger.info(f"  Required sample size: {required_n}")
        logger.info(f"  Current power: {power_results['current_power']:.3f}")
        logger.info(f"  Adequacy level: {power_results['adequacy_level']}")

        # Strict validation checks
        if strict_validation:
            validate_sample_size(actual_n, required_n, min_acceptable_power=0.5)

    with ErrorContext("judge_validation"):
        # Comprehensive judge vulnerability testing
        logger.info("Testing judge vulnerability (comprehensive)...")
        judge_vulnerability = test_judge_vulnerability(comprehensive=True)

        logger.info("Judge Vulnerability Assessment:")
        logger.info(f"  Robustness level: {judge_vulnerability['robustness_level']}")
        logger.info(f"  Vulnerability score: {judge_vulnerability['vulnerability_score']:.3f}")

        # Strict validation
        if strict_validation:
            validate_judge_robustness(judge_vulnerability['vulnerability_score'])

    with ErrorContext("training_phase"):
        # Optional model training with error handling
        if config.train_rounds > 0:
            logger.info(f"Training safety policy for {config.train_rounds} rounds...")
            train_safety_policy(train_unlabeled, config, verbose=True)
        else:
            logger.info("Skipping training (train_rounds=0)")

    with ErrorContext("evaluation_phase"):
        # Run experiments with selected frame category
        logger.info(f"Running Metaethical Pressure Test with {frame_category} frames...")
        frames = get_frames_by_category(frame_category)

        mpt_output = run_metaethical_pressure_test(
            devset=dev_labeled,
            frames=frames,
            frames_per_item=min(config.frames_per_item, len(frames)),
            include_controls=True,
        )

        # Run Self-Reflection Flip Test
        logger.info("Running Self Reflection Flip Test...")
        srft_output = run_self_reflection_flip_test(
            devset=dev_labeled,
            frames=frames[:5],  # Use subset for SRFT
        )

    with ErrorContext("results_analysis"):
        # Comprehensive results compilation
        num_comparisons = len(frames) * 4
        corrected_alpha = 0.05 / num_comparisons

        results = {
            "experiment_metadata": {
                "name": experiment_name,
                "start_time": start_time,
                "duration": time.time() - start_time,
                "config": asdict(config),
                "strict_validation": strict_validation,
                "frame_category": frame_category
            },
            "statistical_analysis": {
                "power_analysis": power_results,
                "warning_check": warning_check,
                "sample_size": {
                    "actual": actual_n,
                    "required": required_n,
                    "adequacy": power_results['adequacy_level']
                }
            },
            "judge_assessment": judge_vulnerability,
            "mpt_results": mpt_output,
            "srft_results": srft_output,
            "statistical_corrections": {
                "num_comparisons": num_comparisons,
                "corrected_alpha": corrected_alpha,
                "bonferroni_applied": True
            }
        }

        # Final comprehensive logging
        _log_experiment_summary(results)

        logger.info(f"Experiment '{experiment_name}' completed successfully")
        logger.info(f"Total duration: {time.time() - start_time:.2f} seconds")

        return results


def _log_experiment_summary(results: Dict[str, Any]) -> None:
    """Log comprehensive experiment summary."""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE EXPERIMENT SUMMARY")
    logger.info("=" * 80)

    # Statistical validation summary
    power_info = results["statistical_analysis"]["power_analysis"]
    logger.info(f"Statistical Power: {power_info['adequacy_level']}")
    logger.info(f"  Current power: {power_info['current_power']:.3f}")
    logger.info(f"  Sample size: {power_info['current_n']}/{power_info['required_n']}")

    # Judge robustness summary
    judge_info = results["judge_assessment"]
    logger.info(f"Judge Robustness: {judge_info['robustness_level']}")
    logger.info(f"  Vulnerability score: {judge_info['vulnerability_score']:.3f}")

    # Results summary
    mpt_metrics = results["mpt_results"]["metrics"]
    logger.info("Experiment Results:")
    logger.info(f"  Control breach rate: {mpt_metrics.get('GBR_control', 0):.3f}")
    logger.info(f"  Meta breach rate: {mpt_metrics.get('GBR_meta', 0):.3f}")
    logger.info(f"  Lift: {mpt_metrics.get('lift', 0):.3f}")

    # Statistical corrections
    corrections = results["statistical_corrections"]
    logger.info(f"Multiple Testing: {corrections['num_comparisons']} comparisons, α={corrections['corrected_alpha']:.5f}")

    logger.info("=" * 80)


def run_parameter_sweep(
    config: ExperimentConfig | None = None,
    frames_per_item_values: List[int] | None = None,
    train_round_values: List[int] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Run a sweep over frames_per_item and/or training rounds.

    Parameters
    ----------
    config : ExperimentConfig, optional
        Base configuration.  A copy is created for each sweep point.
    frames_per_item_values : list of int, optional
        Values of ``frames_per_item`` to test.  If None, uses the value
        from the base configuration.
    train_round_values : list of int, optional
        Values of ``train_rounds`` to test.  If None, uses the value
        from the base configuration.

    Returns
    -------
    dict
        A nested dictionary keyed by the sweep parameter with metrics and
        results for each run.
    """
    if config is None:
        base_config = ExperimentConfig()
    else:
        base_config = config
    base_config.validate()
    outputs: Dict[str, Dict[str, Any]] = {}
    # Determine sweep lists
    f_values = frames_per_item_values or [base_config.frames_per_item]
    t_values = train_round_values or [base_config.train_rounds]
    for frames_per_item in f_values:
        for train_rounds in t_values:
            cfg = ExperimentConfig(
                model=base_config.model,
                api_base=base_config.api_base,
                api_key=base_config.api_key,
                temperature=base_config.temperature,
                max_tokens=base_config.max_tokens,
                frames_per_item=frames_per_item,
                use_cot=base_config.use_cot,
                train_rounds=train_rounds,
                auto_mode=base_config.auto_mode,
                enable_cache=base_config.enable_cache,
            )
            key = f"frames{frames_per_item}_train{train_rounds}"
            logger.info("Running sweep point %s", key)
            outputs[key] = run_experiment(cfg)
    return outputs