# Installation

## Requirements

- Python 3.12 or higher
- pip (Python package installer)

## Basic Installation

```bash
pip install qurankit-core
```

## Optional Dependencies

QuranKit uses optional dependency groups for features that require additional packages:

| Extra | Purpose | Packages |
|-------|---------|----------|
| `cli` | Command-line interface | `click`, `rich` |
| `tanzil` | Tanzil text dataset downloader | `requests` |
| `qac` | QAC morphology provider | `lxml` |
| `mcp` | MCP (Model Context Protocol) server | `mcp` |
| `dev` | Development tools | `pytest`, `ruff`, `mypy` |

### Install with extras

```bash
# For CLI usage
pip install "qurankit-core[cli]"

# For Tanzil dataset downloading
pip install "qurankit-core[tanzil]"

# For full development environment
pip install "qurankit-core[cli,tanzil,qac,mcp,dev]"

# Or install everything
pip install "qurankit-core[all]"
```

## Installing from Source

```bash
git clone https://github.com/AdakHaddad/qurankit.git
cd qurankit
pip install -e ".[dev]"
```

## Verifying Installation

```bash
# Check package version
python -c "import qurankit; print(qurankit.__version__)"

# Check available CLI commands (if cli extra installed)
qurankit --help
```

## Dataset Installation

QuranKit does not bundle Qur'anic text datasets due to licensing. You must install datasets separately:

### Tanzil Text Edition (CC-BY-3.0)

```bash
# Download and install Tanzil text
qurankit dataset install tanzil --edition simple --version 1.0.0

# Or with specific edition
qurankit dataset install tanzil --edition uthmani --version 1.0.0
```

### QAC Morphology (GPL + Non-commercial FAQ)

```bash
# Download and install QAC morphology data
qurankit dataset install qac --version 2.0
```

!!! note "Licensing"
    - **Tanzil**: CC-BY-3.0 — Attribution required, verbatim text only
    - **QAC**: GPL + FAQ non-commercial restriction — Optional adapter only
    - See [Dataset Evaluation](../reference/datasets.md) for full details

## Offline Usage

After datasets are installed, QuranKit works completely offline:

```python
from qurankit import Quran

# No network access required
quran = Quran.load()  # Uses locally installed datasets
```

## Troubleshooting

### Package not found

If you get `ModuleNotFoundError: No module named 'qurankit'`, ensure:

1. You're using the correct package name: `qurankit-core` on PyPI, but import as `qurankit`
2. Your virtual environment is activated
3. The package is installed: `pip list | grep qurankit`

### Dataset not found

If `Quran.load()` fails with dataset not found:

1. Run `qurankit dataset list` to see available datasets
2. Install a dataset: `qurankit dataset install tanzil`
3. Check data directory: `qurankit config show`

### Permission errors

If you get permission errors during dataset installation:

```bash
# Use a custom data directory
export QURANKIT_DATA_DIR=~/qurankit-data
qurankit dataset install tanzil
```

## Next Steps

- [Quick Start →](quickstart.md)
- [Configuration →](configuration.md)
- [Dataset Management →](../user-guide/datasets.md)
