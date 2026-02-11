# Configuration

Advanced configuration options for Finbot.

## Configuration System

Finbot uses [Dynaconf](https://www.dynaconf.com/) for environment-aware configuration. Settings are loaded from YAML files based on the `DYNACONF_ENV` environment variable.

## Configuration Files

Located in `config/` directory:

- `settings.yaml`: Base settings (all environments)
- `development.yaml`: Development overrides
- `production.yaml`: Production overrides
- `.env`: Environment variables (gitignored)

## Environment Selection

```bash
# Development (default)
export DYNACONF_ENV=development

# Production
export DYNACONF_ENV=production
```

## Common Settings

### Threading

```yaml
# config/development.yaml
threading:
  min_threads: 1
  max_threads: null  # Auto-detect
  reserved_threads: 2  # Leave 2 cores for system
```

### Logging

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  json_output: true
  file_rotation_mb: 5
  file_backup_count: 3
```

## API Keys

Store API keys in `config/.env`:

```bash
# config/.env
ALPHA_VANTAGE_API_KEY=your_key_here
NASDAQ_DATA_LINK_API_KEY=your_key_here
US_BUREAU_OF_LABOR_STATISTICS_API_KEY=your_key_here
GOOGLE_FINANCE_SERVICE_ACCOUNT_CREDENTIALS_PATH=/path/to/creds.json
```

Keys are loaded lazily (only when needed).

## Python API

Access settings in code:

```python
from config import settings, settings_accessors

# Get threading config
max_threads = settings_accessors.MAX_THREADS

# Get API key (raises OSError if not set)
api_key = settings_accessors.get_alpha_vantage_api_key()

# Access any setting
log_level = settings.logging.level
```

## See Also

- [Getting Started](getting-started.md) - Basic setup
- [config Module](../api/config.md) - Configuration API reference
