# Installation

Detailed installation instructions for Finbot.

## System Requirements

- **Python**: >=3.11, <3.15
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 2GB for installation + data storage

## Installation Methods

### Method 1: uv (Recommended)

uv provides fast, reliable dependency management and environment isolation:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/jerdaw/finbot.git
cd finbot

# Install the full contributor environment (creates .venv automatically)
uv sync --all-extras

# Minimal CLI/runtime only
# uv sync

# Activate environment (optional, but recommended)
source .venv/bin/activate  # On Linux/Mac
.venv\Scripts\activate     # On Windows

# Set environment
export DYNACONF_ENV=development

# Verify installation
DYNACONF_ENV=development finbot --version
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

# Install the full contributor environment
pip install -e '.[dashboard,web,nautilus,notebooks]'

# Minimal CLI/runtime only
# pip install -e .

# Set environment
export DYNACONF_ENV=development

# Verify
DYNACONF_ENV=development finbot --version
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

For development and local CI parity:

```bash
uv sync --all-extras
```

For a minimal runtime install:

```bash
uv sync
```

Install a specific optional surface only when you need it:

```bash
uv sync --extra dashboard
uv sync --extra web
uv sync --extra nautilus
uv sync --extra notebooks
```

### Verify Installation

Run the test suite:

```bash
DYNACONF_ENV=development uv run pytest -v
```

Expected: the suite completes without failures.

## Troubleshooting

See [Getting Started - Common Issues](getting-started.md#common-issues) for help with installation problems.
