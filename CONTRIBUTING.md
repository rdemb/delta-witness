# Contributing

DeltaWitness is an evidence-first security research prototype. Contributions are welcome when they preserve narrow claims, reproducibility, and fail-closed behavior.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --no-deps -e .
python -m unittest discover -s tests -v
./scripts/demo.sh
python scripts/validate_public_tree.py
```

## Pull-request requirements

A pull request should include:

1. a precise problem statement;
2. a regression test that fails before the change and passes after it;
3. documentation of every new trust assumption;
4. updates to the threat model when execution or publication boundaries change;
5. no unsupported claim of security, correctness, causality, or novelty;
6. disclosure of material AI assistance;
7. confirmation that no credentials, command-line secrets, private paths, sensitive output fingerprints, raw sensitive logs, or embargoed findings are present.

Do not weaken a test, bypass a failing gate, or broaden a claim merely to make CI pass.

## Design standard

Prefer deterministic checks to model judgment. Keep the command runner shell-free. New execution capabilities require explicit design review and tests for failure behavior.

Generated code is accepted, but the contributor remains responsible for understanding, reviewing, testing, and maintaining it.
