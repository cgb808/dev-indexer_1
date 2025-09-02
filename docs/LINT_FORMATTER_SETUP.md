# Python Linting and Formatting

Recommended tools for this workspace:

## 1. Ruff (Fast Linter + Formatter)
- Install: `pip install ruff`
- Usage: `ruff check .` and `ruff format .`
- Add to CI: `ruff check . --output-format=github`

## 2. Black (Formatter)
- Install: `pip install black`
- Usage: `black .`

## 3. isort (Import Sorter)
- Install: `pip install isort`
- Usage: `isort .`

## 4. Flake8 (Linter)
- Install: `pip install flake8`
- Usage: `flake8 .`

## 5. Editor Integration
- VS Code: Install Python, Ruff, and Black extensions for auto-formatting and linting.
- Add to `.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true
}
```

## 6. Pre-commit Hooks (Optional)
- Install: `pip install pre-commit`
- Add `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
```
- Run: `pre-commit install`

---
See `docs/REMOTE_DB_ACCESS.md` for DB security. Use these tools for clean, reliable Python code.
