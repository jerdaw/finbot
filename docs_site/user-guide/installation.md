# Installation

Detailed installation instructions for Finbot.

## System Requirements

- **Python**: >=3.11, <3.15
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 2GB for installation + data storage

## Installation Methods

### Method 1: Poetry (Recommended)

Poetry provides the best dependency management and environment isolation:

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install dependencies
uv sync

# Activate environment
poetry shell

# Verify installation
finbot --version
python -c "import finbot; print('Success!')"
```

### Method 2: pip with venv

Standard Python virtual environment approach:

```bash
# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install package
pip install -e .

# Verify
finbot --version
```

## Post-Installation

### Configure Environment

```bash
# Set environment variable
export DYNACONF_ENV=development  # or production

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export DYNACONF_ENV=development' >> ~/.bashrc
```

### Install Optional Dependencies

For development:

```bash
uv sync
```

For documentation building:

```bash
uv sync
```

### Verify Installation

Run the test suite:

```bash
uv run pytest -v
```

Expected: All 80 tests pass.

## Troubleshooting

See [Getting Started - Common Issues](getting-started.md#common-issues) for help with installation problems.
