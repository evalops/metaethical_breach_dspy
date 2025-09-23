# Setting Up OpenAI API for Robust Judge Models

## Why This Matters
Our testing revealed that the local judge model (gpt-oss:20b) is **vulnerable to metaethical manipulation**, with accuracy dropping from 100% to 66.7% when philosophical framing is added. This compromises all our safety metrics.

## Setup Instructions

### 1. Get your OpenAI API Key
- Go to https://platform.openai.com/api-keys
- Create a new key
- Copy the key (starts with `sk-`)

### 2. Add to Environment
Choose one method:

#### Option A: Export in terminal (temporary)
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

#### Option B: Add to .env file (permanent)
Edit `.env` file and add:
```
OPENAI_API_KEY=sk-your-key-here
```

#### Option C: Add to shell profile (permanent)
Add to `~/.zshrc` or `~/.bashrc`:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Test Connection
```bash
.venv/bin/python test_openai.py
```

### 4. Run Improved Experiments

With GPT-4 as judge:
```bash
JUDGE_MODEL="openai/gpt-4o-mini" .venv/bin/python scripts/run_experiment.py
```

With GPT-4-turbo as judge (more expensive but most robust):
```bash
JUDGE_MODEL="openai/gpt-4-turbo" .venv/bin/python scripts/run_experiment.py
```

## Model Recommendations

### For Judge (evaluating responses):
- **Best:** `openai/gpt-4-turbo` or `openai/gpt-4o` - Most robust against manipulation
- **Good:** `openai/gpt-4` - Solid performance
- **Budget:** `openai/gpt-4o-mini` - Cheaper but test for vulnerability first
- **Avoid:** `gpt-3.5-turbo` - Likely vulnerable to manipulation

### For Test Subject (being evaluated):
- Continue using Ollama models (dolphin-mistral, tinyllama, etc.)
- Or test OpenAI models to compare vulnerability

## Cost Estimates
- GPT-4-turbo: ~$0.01-0.03 per experiment item
- GPT-4o-mini: ~$0.001-0.003 per experiment item
- Full experiment run: ~$0.50-2.00 depending on model

## Validation
After setup, test judge robustness:
```bash
JUDGE_MODEL="openai/gpt-4o-mini" .venv/bin/python test_judge_vulnerability_fixed.py
```

Look for:
- Baseline accuracy: Should be 100%
- Framed accuracy: Should stay >90%
- If accuracy drop >10%, try a more sophisticated model