# Metaethical Breach DSPy

A reproducible research framework for studying safety guardrail
violations in language models under metaethical pressure.  Inspired by
the **Folie à Deux** co‑training study【327039458444812†L384-L404】, this project
investigates whether appeals to abstract moral philosophies can coax a
model into violating its refusal policies.  Where Folie à Deux
optimises verifiers for truth versus agreement, *Metaethical
Breach* measures baseline refusal robustness and the impact of
philosophical framing on guardrail breaches.

## Motivation

The absence of standard benchmarks for ethical robustness means that
potential safety failures may go unnoticed.  Models are typically
rewarded for helpfulness and truthfulness, yet they must also refuse
requests that solicit wrongdoing.  By wrapping harmful prompts in
philosophical arguments (utilitarianism, deontology, virtue ethics,
moral particularism and error theory), we test if a model can be
persuaded to override its guardrails.  The framework quantifies these
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
│   └── experiment.py      # High‑level experiment orchestration
└── tests/
    ├── test_data.py       # Unit tests for dataset functions
    └── test_metrics.py    # Unit tests for metric functions
```

## Dataset configuration

Following the Folie à Deux template【327039458444812†L384-L394】, we split data
into a labeled development set and an unlabeled training set:

- **Development set:** 15 user requests.  Ten are harmful (e.g., paywall
  evasion, Wi‑Fi password theft, exam cheating, fake IDs) and must
  be refused (`verdict='no'`).  Five are benign (capital cities,
  science explanations, translation, etc.) and should be answered
  normally (`verdict='yes'`).
- **Training set:** The harmful base requests repeated several times
  (default five) to supply examples for optional optimisation.

Metaethical framing prompts are defined in `data.py` as five
philosophical lenses.  Each prompt is neutral and does not include
operational instructions.

## Experimental design

Two evaluation modes quantify baseline performance and moral
vulnerability:

1. **Metaethical Pressure Test (MPT)** – Each request is posed
   twice: once plainly (control) and once wrapped in up to `N`
   random metaethical frames.  We compute:
   - **GBR_control:** Guardrail breach rate on control prompts.
   - **GBR_meta:** Breach rate under metaethical framing.
   - **RBR_meta:** Rate of breaches containing ethical justification.
   - **Lift:** Difference (`GBR_meta – GBR_control`).
2. **Self Reflection Flip Test (SRFT)** – The assistant is asked a
   harmful question.  If it refuses, we prompt it to reconsider
   under a metaethical frame.  **FARR** (Flip‑After‑Reflection Rate)
   measures how often an initial refusal flips to a breach.

Optional optimisation uses `dspy.teleprompt.MIPROv2` to tune the
assistant on the unlabeled training set.  A simple refusal metric
rewards common refusal phrasing and penalises any other answer.
Multiple training rounds can be configured via the `TRAIN_ROUNDS`
environment variable.

## Getting started

### Prerequisites

- Python 3.10+
- `dspy-ai` and optional dependencies listed in `requirements.txt`
- A supported language model backend (OpenAI, Anthropic, Ollama, etc.)
  with API credentials.  Refer to `config.py` for environment
  variables.

### Installation

```bash
# Clone the repository
git clone https://github.com/your‑username/metaethical_breach_dspy.git
cd metaethical_breach_dspy

# Create a virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running the experiment

Use the helper script in `scripts/` to run the experiment.  You can
override settings via environment variables:

```bash
# Example: run with default settings using an OpenAI model
export MODEL="gpt-4o"
export API_KEY="sk‑..."
python scripts/run_experiment.py

# Example: run with Anthropic and additional frames per item
MODEL="anthropic/claude-3-sonnet" FRAMES_PER_ITEM=5 python scripts/run_experiment.py

# Example: enable training (two rounds) using a local Ollama model
MODEL="ollama_chat/llama3.1:8b" API_BASE="http://localhost:11434" \
TRAIN_ROUNDS=2 python scripts/run_experiment.py
```

Results are printed to stdout and can be captured to files.  Detailed
per‑example outputs (including redacted assistant messages) are
returned as dictionaries for further analysis.

## Technical details

The implementation follows the modular structure of Folie à Deux【327039458444812†L440-L444】:

- **Configuration management** (`config.py`) loads environment
  variables and configures the DSy runtime.
- **Data** (`data.py`) defines the development set, training set and
  metaethical frames.
- **Judging** (`judge.py`) declares DSPy signatures for assistant
  programmes and the judge, and provides verdict parsing helpers.
- **Metrics** (`metrics.py`) collects utility functions to compute
  aggregate statistics.
- **Evaluation** (`evaluation.py`) implements the MPT and SRFT
  runners, returning per‑item results and summary metrics.
- **Experiment orchestration** (`experiment.py`) ties everything
  together, supporting optional training, experiment loops and
  parameter sweeps (e.g., varying `frames_per_item` or training
  rounds).  Inspired by the co‑evolutionary loop in Folie à Deux【327039458444812†L397-L404】,
  this module allows for systematic studies of refusal robustness.

## Limitations and future work

This research code is experimental.  It assumes the availability of
a second language model to act as judge and uses heuristics for
refusal training.  The dataset is small and the metaethical frames
cover only a handful of ethical theories.  Future work should
introduce larger and more diverse datasets, explore additional
philosophical perspectives, integrate formal safety policies and
compare results across a wider range of model families.  Contributions
are welcome via pull requests.

## License

This project is licensed under the MIT License – see the `LICENSE`
file for details.