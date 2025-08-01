# Contributing to irouter

Thank you for your interest in contributing to `irouter`! We aim to make accessing 100's of LLMs as simple as possible.

Openrouter.ai is used under the hood to access LLMs through their API.

## Getting Started

1. Fork the repository
2. Clone your fork and install in development mode. Preferable use `uv` to manage dependencies:
```bash
git clone https://github.com/carlolepelaars/irouter.git
cd irouter
pip install uv
uv sync --all-extras
uv pip install -e .
```

## Ways to Contribute

- **Fix bugs**: Search existing issues first, then create detailed bug reports.
- **Add features**: Discuss new features in GitHub Issues before implementing.
- **Improve documentation**: Add examples, clarify docstrings, or enhance guides.
- **Write tests**: Increase test coverage for existing functionality.

## Development Guidelines

### Code Standards
- Use appropriate type hints (Python 3.10+ syntax)
- Keep docstrings concise but complete (reStructured format)
- Add new dependencies via `uv add <package>`

### Before Committing Code
Run quality checks:
```bash
uv run ruff format
uv run ruff check
uv run pytest -s
```

### Pull Requests
- Keep PRs focused on a single change
- Include tests for new features and bug fixes
- Update documentation as needed
- Reference related issues

## Feature Requests

Before implementing new features:
1. Open a GitHub Issue to discuss the proposal

2. Get community feedback

3. Consider maintenance burden and API consistency

## Bug Reports

Include:

- Error messages and stack traces
- Code that reproduces the issue
- Environment details (Python version, OS)
- Expected vs actual behavior

## Questions?

Open a GitHub Issue for questions about the codebase or potential contributions.