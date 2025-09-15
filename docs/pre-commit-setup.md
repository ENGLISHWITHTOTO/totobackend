# Pre-commit Setup Guide

This guide explains how to set up and use pre-commit hooks for the Toto Backend project.

## What is Pre-commit?

Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. It helps ensure code quality by running various checks and formatters before each commit.

## Installation

### 1. Install Dependencies

```bash
# Install development dependencies including pre-commit
pip install -r requirements-dev.txt

# Or if using uv (recommended)
uv pip install -r requirements-dev.txt
```

### 2. Install Pre-commit Hooks

```bash
# Install the pre-commit hooks
pre-commit install

# Install commit message hook (optional but recommended)
pre-commit install --hook-type commit-msg
```

### 3. Update Hooks (Optional)

```bash
# Update all hooks to latest versions
pre-commit autoupdate
```

## Configuration

The pre-commit configuration is defined in `.pre-commit-config.yaml` and includes:

### Code Quality Hooks

- **Black**: Python code formatting
- **isort**: Import sorting
- **flake8**: Python linting
- **mypy**: Type checking
- **pylint**: Additional Python linting
- **bandit**: Security scanning

### Django-specific Hooks

- **django-upgrade**: Automatically upgrade Django code

### General Hooks

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-json**: Validate JSON files
- **debug-statements**: Detect debug statements
- **detect-private-key**: Detect private keys

### File-specific Hooks

- **hadolint**: Dockerfile linting
- **prettier**: YAML/JSON formatting
- **shellcheck**: Shell script linting

## Usage

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black

# Run hooks on staged files only
pre-commit run

# Skip hooks (use with caution)
git commit --no-verify -m "message"
```

### Bypassing Hooks

In rare cases, you might need to bypass pre-commit hooks:

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "Emergency fix"

# Skip specific hook
SKIP=flake8 git commit -m "Skip flake8 for this commit"
```

## Troubleshooting

### Common Issues

1. **Hook fails on first run**

   ```bash
   # Update hooks and try again
   pre-commit autoupdate
   pre-commit run --all-files
   ```

2. **Black/isort conflicts**

   ```bash
   # Run formatters manually
   black .
   isort .
   git add .
   git commit -m "Format code"
   ```

3. **mypy errors**

   ```bash
   # Check mypy configuration
   mypy . --ignore-missing-imports
   ```

4. **Django migration issues**
   ```bash
   # Exclude migrations from certain hooks
   # Migrations are automatically excluded in the config
   ```

### Updating Hooks

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Update specific hook
pre-commit autoupdate --repo https://github.com/psf/black
```

## Configuration Files

### .pre-commit-config.yaml

Main configuration file defining all hooks and their settings.

### pyproject.toml

Contains tool-specific configurations:

- Black settings
- isort settings
- mypy settings

### .flake8

Flake8 configuration (if needed)

## Integration with CI/CD

The pre-commit hooks are also integrated into the CI/CD pipeline in `.github/workflows/ci-cd.yml`:

- Code formatting (Black)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)

## Best Practices

1. **Always run hooks before committing**
2. **Fix issues locally before pushing**
3. **Use meaningful commit messages**
4. **Keep hooks updated**
5. **Don't bypass hooks unless absolutely necessary**

## IDE Integration

### VS Code

Install the "Pre-commit" extension for better integration.

### PyCharm

Configure external tools to run pre-commit commands.

## Team Setup

All team members should:

1. Install pre-commit: `pip install -r requirements-dev.txt`
2. Install hooks: `pre-commit install`
3. Run on all files: `pre-commit run --all-files`

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
