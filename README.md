[![Tests](https://github.com/cmudrc/AutoBoltAgent/actions/workflows/test.yml/badge.svg)](https://github.com/cmudrc/AutoBoltAgent/actions/workflows/test.yml)

# AutoBoltAgent

AutoBoltAgent is a small Python package that provides AI-powered assistance for bolt design tasks. It aims to help
engineers prototype bolt specifications and explore design options programmatically.

Key points:

- Lightweight library packaged under `autoboltagent`.
- Includes example tools for low- and high-fidelity bolt generation and helper inputs.

## Requirements

- Python 3.10+
- (Optional) Conda for easy environment setup — an `environment.yml` is included in the repository.

## Quick start

1. Create and activate a Python environment (optional, using conda):

```bash
# create (first time)
conda env create -f environment.yml
# activate
conda activate autoboltagent
```

2. Install the package in editable mode:

```bash
pip install -e .
```

3. Use the package from Python. Example (interactive):

```python
from autoboltagent import agents, prompts
```
