# Contributing

Thanks for kicking the tires.

## What this repo is
This is a research framework for comparing ERCOT transmission cost allocation methodologies. It is not a tariff recommendation, settlement engine, or policy verdict generator.

## What reviewers should challenge
- Hidden assumptions in methodology implementations
- Whether proxy choices are honestly labeled
- Whether fallback modes are explicit and appropriately downgraded in confidence
- Whether export treatment is applied consistently in net-aware runs
- Whether comparison metrics accidentally smuggle in a preferred answer
- Whether any public artifact leaks licensed data

## Good contribution types
- Clarify methodology definitions
- Tighten validation checks
- Add public-safe synthetic fixtures
- Improve sensitivity coverage
- Correct implementation mistakes against the locked ADRs and methodology specs
- Improve docs, tests, notebooks, and reproducibility

## Data corrections
If a methodology depends on an incorrect public assumption, open an issue with:
1. the file and line range
2. the competing interpretation
3. the public source or protocol citation
4. the practical impact on results

Do not submit licensed Yes Energy or Enverus raw data in issues or pull requests.

## Development
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -v
```

## Pull requests
Please keep PRs narrow.

Include:
- what changed
- why it changed
- what tests you ran
- whether the change affects methodology interpretation, comparison outputs, or only packaging/docs

## Review standard
A contribution is strongest when it improves transparency, not when it makes the framework look prettier.
