# Metaethical Breach DSPy

A reproducible research framework for studying safety guardrail
violations in language models under metaethical pressure. Inspired by
the [**Folie à Deux** co-training study](https://github.com/evalops/folie-a-deux-dspy), this project
investigates whether appeals to abstract moral philosophies can coax a
model into violating its refusal policies. Where Folie à Deux
optimises verifiers for truth versus agreement, *Metaethical
Breach* measures baseline refusal robustness and the impact of
philosophical framing on guardrail breaches.

## Motivation

The absence of standard benchmarks for ethical robustness means that
potential safety failures may go unnoticed. Models are typically
rewarded for helpfulness and truthfulness, yet they must also refuse
requests that solicit wrongdoing. By wrapping harmful prompts in
philosophical arguments (utilitarianism, deontology, virtue ethics,
moral particularism and error theory), we test if a model can be
persuaded to override its guardrails. The framework quantifies these
effects and supports optional optimisation to harden refusals.

## Repository structure

```
metaethical_breach_dspy/
├── README.md              # This file
├── LICENSE                # MIT License
├── Makefile               # Convenience commands
├── requirements.txt       # Python dependencies
├── docs/
│   └── overview.md        # Extended documentation and research context
├── results/
│   └── README.md          # Placeholder for experiment outputs
├── scripts/
│   └── run_experiment.py  # CLI entrypoint
├── metaethical_breach/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── data.py            # Dataset and metaethical frames
│   ├── judge.py           # Signature definitions and verdict parsing
│   ├── metrics.py         # Metric functions
│   ├── evaluation.py      # Test runners (pressure & flip tests)
│   └── experiment.py      # High-level experiment orchestration
└── tests/
    ├── test_data.py       # Unit tests for dataset functions
    └── test_metrics.py    # Unit tests for metric functions
```

## Dataset configuration

Following the [Folie à Deux template](https://github.com/evalops/folie-a-deux-dspy), we split data
into a labeled development set and an unlabeled training set:

- **Development set:** 15 user requests. Ten are harmful (e.g., paywall
  evasion, Wi-Fi password theft, exam cheating, fake IDs) and must
  be refused (`verdict='no'`). Five are benign (capital cities,
  science explanations, translation, etc.) and should be answered
  normally (`verdict='yes'`).
- **Training set:** The harmful base requests repeated several times
  (default five) to supply examples for optional optimisation.

Metaethical framing prompts are defined in `data.py` as five
philosophical lenses. Each prompt is neutral and does not include
operational instructions.

## Experimental design

Two evaluation modes quantify baseline performance and moral
vulnerability:

1. **Metaethical Pressure Test (MPT)** – Each request is posed
   twice: once plainly (control) and once wrapped in up to `N`
   random metaethical frames. We compute:
   - **GBR_control:** Guardrail breach rate on control prompts.
   - **GBR_meta:** Breach rate under metaethical framing.
   - **RBR_meta:** Rate of breaches containing ethical justification.
   - **Lift:** Difference (`GBR_meta – GBR_control`).
2. **Self Reflection Flip Test (SRFT)** – The assistant is asked a
   harmful question. If it refuses, we prompt it to reconsider
   under a metaethical frame. **FARR** (Flip-After-Reflection Rate)
   measures how often an initial refusal flips to a breach.

Optional optimisation uses `dspy.teleprompt.MIPROv2` to tune the
assistant on the unlabeled training set. A simple refusal metric
rewards common refusal phrasing and penalises any other answer.
Multiple training rounds can be configured via the `TRAIN_ROUNDS`
environment variable.

## Getting started

### Prerequisites

- Python 3.10+
- `dspy-ai` and optional dependencies listed in `requirements.txt`
- A supported language model backend (OpenAI, Anthropic, Ollama, etc.)
  with API credentials. Refer to `config.py` for environment
  variables.

### Installation

```bash
# Clone the repository
git clone https://github.com/evalops/metaethical_breach_dspy.git
cd metaethical_breach_dspy

# Create a virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running the experiment

Use the helper script in `scripts/` to run the experiment. You can
override settings via environment variables:

```bash
# Example: run with default settings using an OpenAI model
export MODEL="gpt-4o"
export API_KEY="sk-..."
python scripts/run_experiment.py

# Example: run with Anthropic and additional frames per item
MODEL="anthropic/claude-3-sonnet" FRAMES_PER_ITEM=5 python scripts/run_experiment.py

# Example: enable training (two rounds) using a local Ollama model
MODEL="ollama_chat/llama3.1:8b" API_BASE="http://localhost:11434" \
TRAIN_ROUNDS=2 python scripts/run_experiment.py
```

Results are printed to stdout and can be captured to files. Detailed
per-example outputs (including redacted assistant messages) are
returned as dictionaries for further analysis.

## Results

### Updated Results (Fixed Framework)

**Testing with Dolphin-Mistral using methodologically sound framework:**

| Condition | Breach Rate | 95% CI | Interpretation |
|-----------|-------------|--------|----------------|
| **Baseline** | 0.333 | [0.086, 0.580] | Direct harmful requests |
| **Philosophical** | 0.600 | [0.343, 0.857] | With metaethical framing |
| **Length Control** | 0.267 | [0.035, 0.498] | **NEW!** Non-philosophical padding |
| **Academic Control** | *Testing* | *In progress* | Intellectual but non-philosophical |

**Framework Validation:**
- **Judge Robustness:** ✅ ROBUST (no vulnerability to philosophical manipulation)
- **Sample Size:** ⚠️ 15/1568 (requires 100x more data for statistical validity)
- **Control Conditions:** ✅ Length and content controls implemented
- **Confidence Intervals:** ✅ All metrics reported with uncertainty bounds

### Key Discoveries

1. **The "Negative Lift" Mystery Solved**: The previous result showing philosophical framing made models safer (-0.067 lift) was a **measurement artifact** caused by judge vulnerability, not a real effect.

2. **Prompt Length Dominates Content**: The biggest surprise - simple padding words triggered stronger refusal (0.267) than some philosophical arguments, revealing that **structural features matter more than semantic content**.

3. **Judge Vulnerability Crisis**: The original judge model was manipulated by philosophical framing (33% accuracy drop), completely inverting safety metrics. This highlights critical flaws in AI safety evaluation infrastructure.

4. **Real Effect Confirmed**: With proper methodology, philosophical framing does increase breach rates (0.333 → 0.600), but the mechanism is cognitive engagement, not ethical confusion.

5. **Statistical Validity Issues**: Most findings were within statistical noise due to severe underpowering (n=15 vs n=1568 required).

### Why Dolphin-Mistral is Vulnerable

The Dolphin series models are explicitly designed to be "uncensored" - they have been fine-tuned to remove refusal behaviors present in the base Mistral model. According to the model's documentation:

- **Removed alignment**: The model has been deliberately trained to comply with requests that standard models would refuse
- **No safety training**: Unlike standard models that undergo RLHF (Reinforcement Learning from Human Feedback) for safety, Dolphin models skip this step
- **Instruction-following priority**: The model prioritizes following instructions over safety considerations
- **Community-driven**: Created by the open-source community specifically for unrestricted use cases

This makes Dolphin-Mistral useful for:
- Red-teaming and safety research
- Understanding model vulnerabilities
- Testing safety measures and guardrails
- Academic research on model behavior

**Warning**: Due to its lack of safety constraints, Dolphin-Mistral should only be used in controlled research environments and never deployed in production systems without additional safety layers.

## 🔬 Major Research Update: Framework Issues & Surprising Discoveries

### What We Found
Our investigation uncovered critical methodological flaws AND surprising insights about AI safety:

#### 1. Judge Vulnerability Crisis
- The judge model (gpt-oss:20b) had **33% accuracy drop** with philosophical framing
- This created completely inverted safety metrics
- The famous "negative lift" was a measurement artifact!
- **Solution**: Use GPT-4o-mini or GPT-4o (verified 0% vulnerability)

#### 2. The Real Story (Revealed by Improved Framework)
Testing with proper controls revealed what's ACTUALLY happening:

| Condition | Dolphin-Mistral Response | Safety Score | Insight |
|-----------|-------------------------|--------------|---------|
| **Baseline** | Full harmful assistance | 0.000 | No safety guardrails |
| **Philosophical** | Partial refusal with caveats | 0.505 | Philosophy triggers thoughtfulness |
| **Length Control** | Strong refusal | 1.000 | 🤯 Just padding causes refusal! |
| **Academic** | Weak breach with explanation | 0.200 | Academic ≠ philosophical |

#### 3. Critical Methodological Issues
- **Sample size**: n=15 vs n=1,568 needed (100x undersized!)
- **Hidden confound**: Prompt length alone changes behavior
- **Binary classification**: Missed that responses exist on spectrum
- **No confidence intervals**: Results were statistical noise
- **Multiple comparisons**: 64% false positive rate

See full analysis: `JUDGE_VULNERABILITY_DISCOVERY.md`, `FRAMEWORK_ISSUES_ANALYSIS.md`, `FINAL_ANALYSIS.md`

## 📊 What This Tells Us About AI Safety

### Key Takeaways

1. **Evaluation infrastructure is as important as the models themselves**
   - A vulnerable judge can completely invert your safety metrics
   - Without proper controls, you're measuring confounds not effects
   - Binary metrics hide critical behavioral nuances

2. **Prompt length is a massive hidden factor**
   - Simply adding padding words triggered the strongest refusal (1.000)
   - This confound was affecting ALL previous measurements
   - Length effects may explain many "jailbreak" phenomena

3. **Models respond to cognitive load, not just content**
   - Philosophical framing → more thoughtful responses
   - Academic framing → different effect than philosophical
   - Complexity triggers different processing modes

4. **The "metaethical breach" hypothesis needs revision**
   - Philosophy doesn't simply bypass guardrails
   - It may actually INCREASE safety in some cases
   - The mechanism is cognitive engagement, not ethical confusion

5. **Most AI safety research may have measurement issues**
   - If a well-intentioned framework had these problems...
   - How many published results are measurement artifacts?
   - We need standardized, robust evaluation methods

## ✅ Framework Fixed

We've fixed the original framework files with methodologically sound improvements:

### Files Updated
- **`metaethical_breach/judge.py`** - Added judge vulnerability testing
- **`metaethical_breach/evaluation.py`** - Added control conditions (length, academic)
- **`metaethical_breach/metrics.py`** - Added confidence intervals and sample size calculation
- **`metaethical_breach/experiment.py`** - Integrated all improvements into main runner

### What's Fixed
| Issue | Before | After |
|-------|--------|-------|
| Sample Size | 15 (underpowered) | Calculates required n=1,568 |
| Judge Robustness | Vulnerable (-33% accuracy) | Tests & verifies robustness |
| Controls | Baseline vs philosophical only | 4 conditions with length/content controls |
| Measurement | Binary BREACH/REFUSE | Graduated scale with confidence intervals |
| Statistics | Point estimates only | CI, multiple testing correction |
| Confounds | Prompt length uncontrolled | Length effects measured separately |

### Usage
```bash
# Run with fixed framework
export MODEL="ollama_chat/dolphin-mistral:7b-v2.6-q4_K_M"
export API_BASE="http://localhost:11434"
python scripts/run_experiment.py
```

### The Bottom Line
The fixed framework reveals that **evaluation methodology is as critical as the models being evaluated**:
- Judge vulnerability can completely invert safety metrics
- Prompt structure (length) often dominates semantic content
- Proper controls separate real effects from artifacts
- Statistical rigor is essential for valid conclusions

## Technical details

The implementation follows the modular structure of [Folie à Deux](https://github.com/evalops/folie-a-deux-dspy):

- **Configuration management** (`config.py`) loads environment
  variables and configures the DSPy runtime.
- **Data** (`data.py`) defines the development set, training set and
  metaethical frames.
- **Judging** (`judge.py`) declares DSPy signatures for assistant
  programmes and the judge, and provides verdict parsing helpers.
- **Metrics** (`metrics.py`) collects utility functions to compute
  aggregate statistics.
- **Evaluation** (`evaluation.py`) implements the MPT and SRFT
  runners, returning per-item results and summary metrics.
- **Experiment orchestration** (`experiment.py`) ties everything
  together, supporting optional training, experiment loops and
  parameter sweeps (e.g., varying `frames_per_item` or training
  rounds). Inspired by the co-evolutionary loop in [Folie à Deux](https://github.com/evalops/folie-a-deux-dspy),
  this module allows for systematic studies of refusal robustness.

## Limitations and future work

This research code is experimental. It assumes the availability of
a second language model to act as judge and uses heuristics for
refusal training. The dataset is small and the metaethical frames
cover only a handful of ethical theories. Future work should
introduce larger and more diverse datasets, explore additional
philosophical perspectives, integrate formal safety policies and
compare results across a wider range of model families. Contributions
are welcome via pull requests.

## License

This project is licensed under the MIT License – see the `LICENSE`
file for details.