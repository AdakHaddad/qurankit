# Contributing to QuranKit

Thank you for your interest in contributing to QuranKit! This guide covers our development workflow, coding standards, and contribution process.

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- pip

### Clone and Install

```bash
git clone https://github.com/AdakHaddad/qurankit.git
cd qurankit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[dev,cli,tanzil,qac,mcp]"
```

### Verify Setup

```bash
# Run tests
pytest tests/ -v

# Check code style
ruff check src/
ruff format src/ --check

# Type checking
mypy src/
```

## Coding Standards

### Python Style

- **Formatter**: Ruff (configured in `pyproject.toml`)
- **Line length**: 100 characters
- **Quotes**: Double quotes
- **Type hints**: Required for all public functions
- **Docstrings**: Google style

### Type Hints

```python
# Good
def search_text(query: str, mode: SearchMode = "broad", limit: int = 100) -> list[SearchResult]:
    ...

# Avoid
def search_text(query, mode="broad", limit=100):
    ...
```

### Docstrings

```python
def lookup_root(self, root_form: str, limit: int | None = None) -> list[VocabularyOccurrence]:
    """Look up all Qur'anic occurrences of an Arabic root.

    Args:
        root_form: The Arabic root (e.g., "ر ح م" or "رَحْمَة").
        limit: Maximum number of occurrences to return.

    Returns:
        List of vocabulary occurrences sorted by surah/ayah.

    Raises:
        DatasetNotFoundError: If QAC morphology data is not installed.
    """
```

### Imports

```python
# Standard library first
import json
from pathlib import Path
from typing import Optional

# Third-party
import pydantic
from pydantic import BaseModel

# Local
from qurankit.models import Surah
from qurankit.search import SearchEngine
```

## Testing Requirements

### Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Unit | `tests/unit/` | Individual functions/classes |
| Integration | `tests/integration/` | Dataset loaders, pipelines |
| Golden | `tests/fixtures/` | Reviewed Arabic examples |

### Writing Tests

```python
# tests/unit/test_my_feature.py
import pytest
from qurankit import Quran
from qurankit.models import Surah

class TestMyFeature:
    def test_surah_creation(self):
        surah = Surah(number=1, name_arabic="الفاتحة", ...)
        assert surah.number == 1
        assert surah.name_arabic == "الفاتحة"

    @pytest.fixture
    def quran_with_data(self):
        # Use fixture for integration tests
        quran = Quran.load()
        return quran

    def test_search_returns_results(self, quran_with_data):
        results = quran_with_data.search("بسم الله", mode="broad")
        assert len(results) > 0
```

### Arabic Test Fixtures

- Use real Qur'anic text from installed datasets
- Never fabricate Arabic text
- Preserve source representation exactly
- Document fixture source and version

```python
# tests/fixtures/arabic_examples.py
# Source: Tanzil Simple v1.0.0
FATIHAH_AYAH_1 = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
FATIHAH_AYAH_1_NORMALIZED_BROAD = "بسم الله الرحمن الرحيم"
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit only
pytest tests/unit/ -v

# Integration only
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=qurankit --cov-report=html

# Specific test
pytest tests/unit/test_search.py::TestNormalizationEngine::test_broad_search -v
```

## Git Workflow

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<description>` | `feat/add-tafsir-adapter` |
| Bugfix | `fix/<description>` | `fix/search-offset-bug` |
| Docs | `docs/<description>` | `docs/update-api-reference` |
| Refactor | `refactor/<description>` | `refactor/vocabulary-caching` |

### Commit Messages

Follow Conventional Commits:

```
feat: add tafsir adapter interface

- Add TafsirAdapter abstract base class
- Implement FileBasedTafsirAdapter
- Add registry for multiple tafsir sources
- Include sample data from public domain sources

Closes #123
```

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite: `pytest tests/ -v`
4. Run linting: `ruff check src/` and `ruff format src/ --check`
5. Run type checking: `mypy src/`
6. Update documentation if needed
7. Submit PR with description of changes
8. Address review feedback
9. Squash and merge (maintainers)

## Documentation Standards

### When to Update Docs

- New public API → Update API reference
- New feature → Add user guide page
- Behavior change → Update relevant guides
- New dataset → Update dataset evaluation

### Documentation Style

- Use clear, concise language
- Include code examples for all features
- Document parameters, returns, exceptions
- Note limitations and known issues
- Use admonitions for warnings/notes

```markdown
!!! note "Important"
    This feature requires QAC morphology data.

!!! warning "License"
    QAC data has non-commercial restrictions.
```

## Data and Licensing

### Adding Datasets

1. **Verify license** — Confirm redistribution rights
2. **Document provenance** — Source, version, retrieval date
3. **Create manifest** — Include checksum, license, metadata
4. **Build adapter** — Transform to QuranKit schema
5. **Add validation** — Verify structure and integrity
6. **Write tests** — Golden tests for known references

### Arabic Text Handling

- Never modify source Arabic text
- Store normalized forms separately
- Track character mappings
- Document normalization rules
- Test edge cases (hamza, alif maqsurah, etc.)

## Release Process

### Versioning

Semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

- [ ] All tests pass
- [ ] Linting clean
- [ ] Type checking clean
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Tag created: `git tag v0.x.y`
- [ ] Published to PyPI
- [ ] GitHub release created

## Code of Conduct

- Be respectful and inclusive
- Focus on technical merit
- Respect religious sensitivities
- Follow Islamic etiquette for Qur'anic content
- No proselytizing or theological debates in technical discussions

## Getting Help

- GitHub Issues: Bug reports, feature requests
- GitHub Discussions: Questions, design discussions
- Email: muqtada@example.com

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md`
- Release notes
- Documentation credits
