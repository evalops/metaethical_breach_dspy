"""Basic tests for the metaethical breach framework."""

import pytest
from metaethical_breach.metrics import calculate_required_sample_size, compute_confidence_interval


def test_sample_size_calculation():
    """Test that sample size calculation works correctly."""
    # Test standard parameters
    n = calculate_required_sample_size(effect_size=0.1, alpha=0.05, power=0.8)
    assert n == 1568, f"Expected 1568, got {n}"
    
    # Test larger effect size needs fewer samples
    n_large = calculate_required_sample_size(effect_size=0.2)
    assert n_large < n, "Larger effect size should need fewer samples"


def test_confidence_interval():
    """Test confidence interval calculation."""
    scores = [0.1, 0.2, 0.3, 0.4, 0.5]
    mean, lower, upper = compute_confidence_interval(scores)
    
    assert 0 <= mean <= 1, "Mean should be between 0 and 1"
    assert lower <= mean <= upper, "CI should contain the mean"
    assert lower >= 0 and upper <= 1, "CI should be valid probability range"


def test_judge_vulnerability_import():
    """Test that judge vulnerability function can be imported."""
    from metaethical_breach.judge import test_judge_vulnerability
    assert callable(test_judge_vulnerability)


def test_evaluation_with_controls():
    """Test that evaluation can be run with controls."""
    from metaethical_breach.evaluation import run_metaethical_pressure_test
    # Just test that function exists and has the right signature
    import inspect
    sig = inspect.signature(run_metaethical_pressure_test)
    assert 'include_controls' in sig.parameters
