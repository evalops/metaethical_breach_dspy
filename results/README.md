This directory is reserved for experiment outputs.  Running the
experiment (see `scripts/run_experiment.py`) will print results to
stdout; you can capture these results into files and store them here
for later analysis.  For example:

```bash
python scripts/run_experiment.py > results/mpt_srft_default.json
```

Please do not commit sensitive API responses.  Consider redacting
assistant messages if they contain harmful or private content.