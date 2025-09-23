# Claude Code Instructions for Metaethical Breach DSPy

## Production Implementation Gaps to Address

### Critical Issues Identified

**1. Sample Size Undermines Claims**
- Current: n=15 vs. ~1,568 needed for statistical significance
- Issue: Results are directional evidence, not robust findings
- Solutions needed:
  - (a) Collect more data for statistical validity, OR
  - (b) Reframe as exploratory, hypothesis-generating research

**2. Evaluation Model Risk**
- Judge vulnerability is a real hazard
- If eval model can be "philosophically persuaded" → false positives
- Need empirical validation of judge robustness, not just claims

**3. Frame Diversity Limitations**
- Current: Five Western-analytic frameworks only
- Missing: Non-Western moral systems
  - Confucian relational ethics
  - Buddhist consequentialism
  - Indigenous ethical frameworks
- Missing: Contemporary applied frames
  - Bioethics
  - Just war theory
  - Corporate ethics

**4. Model Coverage Weakness**
- Current: Only Dolphin-Mistral results shown
- Appears cherry-picked without multi-model validation
- Need results across 2-3 model families:
  - Anthropic (Claude)
  - OpenAI (GPT-4/3.5)
  - Meta (Llama-3)
  - Local (Ollama variants)

**5. Exploit vs. Artifact Ambiguity**
- Unclear if "breach" is from ethical reasoning OR:
  - (a) Longer/more abstract prompts
  - (b) Models trained on philosophy essays defaulting to compliance
- Length and academic controls help but need quantitative evidence they don't collapse the effect

## Implementation Requirements

### Production Standards
- Comprehensive error handling and logging
- Configuration validation with clear error messages
- Type hints throughout codebase
- Robust statistical analysis with proper confidence intervals
- Multi-model testing framework
- Expanded philosophical framework coverage
- Empirical judge vulnerability validation
- Clear separation of exploratory vs. confirmatory findings

### Code Quality
- Professional logging framework
- Configuration management with validation
- Error handling for all external API calls
- Progress tracking for long-running experiments
- Result serialization and analysis tools
- Comprehensive test suite

## Commands for Testing
```bash
# Test framework robustness
make test

# Run experiments
make experiment

# Validate judge models
python scripts/validate_judges.py

# Run multi-model comparison
python scripts/compare_models.py
```

This framework should meet the standards of top-tier AI safety research while being robust enough for production use.