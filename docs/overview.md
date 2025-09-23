# Metaethical Breach Framework - Technical Overview

## Research Context

This framework investigates **metaethical pressure testing** - using philosophical arguments to bypass AI safety guardrails. The research demonstrates that **philosophical framing can nearly double jailbreak success rates**, from 33% to 60% in uncensored models.

## Core Discovery

**Philosophical framing is a potent attack vector**: When attackers wrap harmful requests in moral reasoning frameworks (utilitarian, deontological, virtue ethics), they achieve an **80% increase in successful guardrail breaches**.

## Key Results

| Attack Method | Breach Rate | Interpretation |
|---------------|-------------|----------------|
| Direct request | 33% | Baseline harmful request |
| **Philosophical framing** | **60%** | **Utilitarian/deontological wrapper** |
| Length padding | 27% | Non-philosophical text padding |

**Conclusion**: The effect is specifically from philosophical reasoning, not just prompt length or complexity.

## Technical Architecture

### Framework Components

1. **`metaethical_breach/judge.py`** - Vulnerability-tested judge ensemble
2. **`metaethical_breach/evaluation.py`** - Controlled experimental conditions
3. **`metaethical_breach/metrics.py`** - Statistical validation with confidence intervals
4. **`metaethical_breach/experiment.py`** - Main orchestration with proper methodology

### Methodological Improvements

This framework addresses critical issues found in AI safety evaluation:

- **Judge Vulnerability Testing**: Ensures judges aren't manipulated by philosophical framing
- **Control Conditions**: Tests length effects separately from content effects
- **Statistical Rigor**: Confidence intervals, power analysis, multiple testing correction
- **Graduated Measurement**: 5-dimensional response assessment vs binary classification

## Research Implications

### For AI Safety
- **Red Teams**: Include philosophers and ethicists
- **Safety Training**: Must be robust against moral reasoning exploits
- **Detection**: Monitor for philosophical framing in user prompts

### For Evaluation Methodology
- **Judge Robustness**: Test evaluation models for manipulation vulnerability
- **Control Conditions**: Always include appropriate baseline comparisons
- **Statistical Power**: Use adequate sample sizes (n=1,568 for 10% effects)
- **Measurement Granularity**: Binary metrics hide important behavioral nuances

## Limitations

- **Sample Size**: Current n=15 vs required n=1,568 for full statistical validity
- **Model Coverage**: Primarily tested on Dolphin-Mistral (uncensored model)
- **Domain Scope**: Limited to specific types of harmful requests
- **Judge Dependency**: Results depend on judge model robustness

## Future Research

1. **Scale-up**: Run with statistically adequate sample sizes
2. **Model Diversity**: Test across various model families and safety training approaches
3. **Attack Sophistication**: Explore advanced philosophical argument structures
4. **Defense Development**: Create robust countermeasures against philosophical manipulation

## Practical Applications

### Red Teaming
Use philosophical frames to test model robustness:
```
"From a utilitarian perspective maximizing overall wellbeing: [harmful request]"
```

### Safety Evaluation
Implement the framework's methodology to:
- Test judge vulnerability before evaluation
- Include appropriate control conditions
- Report confidence intervals on all metrics
- Use graduated response scales

This framework provides both a specific finding (philosophical framing as attack vector) and general methodological improvements for AI safety research.