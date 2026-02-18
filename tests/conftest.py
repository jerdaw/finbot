"""Root pytest configuration — applies to the entire test suite.

Sets DYNACONF_ENV before any finbot modules are imported so that
finbot.config loads without raising ValueError on the missing ENV var.
"""

from __future__ import annotations

import os

# Must be set before any finbot.config import happens.
os.environ.setdefault("DYNACONF_ENV", "development")
