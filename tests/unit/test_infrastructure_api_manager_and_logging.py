from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from finbot.config.logging_config import _setup_queue_logging, initialize_logger, prepare_logging_config
from finbot.libs.api_manager import api_manager as global_api_manager
from finbot.libs.api_manager._utils.api import API
from finbot.libs.api_manager._utils.api_manager import APIManager
from finbot.libs.api_manager._utils.api_resource_group import APIResourceGroup
from finbot.libs.logger.setup_queue_logging import setup_queue_logging
from finbot.libs.logger.utils import ColorFormatter, ErrorFilter, LoggingJsonFormatter, NonErrorFilter
from finbot.utils.request_utils.rate_limiter import DEFAULT_RATE_LIMIT
from finbot.utils.request_utils.retry_strategy import DEFAULT_HTTPX_RETRY_KWARGS


class _DummyGroup:
    def __init__(self) -> None:
        self.added: list[API] = []

    def add_api(self, api: API) -> None:
        self.added.append(api)


def test_api_adds_itself_to_resource_group() -> None:
    group = _DummyGroup()
    api = API(
        identifier="test_api",
        resource_group=group,
        base_url="https://example.invalid",
        endpoints=["a", "b"],
    )

    assert group.added == [api]
    assert api.identifier == "test_api"
    assert api.base_url == "https://example.invalid"
    assert api.endpoints == ["a", "b"]


def test_api_resource_group_add_get_and_contains() -> None:
    group = APIResourceGroup(
        identifier="g1",
        rate_limit=DEFAULT_RATE_LIMIT,
        retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
        extra_flag=True,
    )
    api = API(identifier="alpha", resource_group=group)

    assert group.identifier == "g1"
    assert group.get_apis()["alpha"] is api
    assert "alpha" in group
    assert api in group
    assert group.extra_flag is True


def test_api_resource_group_rejects_reserved_kwarg() -> None:
    with pytest.raises(ValueError, match="already exists"):
        APIResourceGroup(
            identifier="g1",
            rate_limit=DEFAULT_RATE_LIMIT,
            retry_strategy_kwargs=DEFAULT_HTTPX_RETRY_KWARGS,
            apis="bad",
        )


def test_api_manager_add_get_and_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = APIManager(auto_load_apis=False, auto_load_resource_groups=False)
    warnings: list[str] = []
    errors: list[str] = []
    monkeypatch.setattr("finbot.libs.api_manager._utils.api_manager.logger.warning", warnings.append)
    monkeypatch.setattr("finbot.libs.api_manager._utils.api_manager.logger.error", errors.append)

    api_without_group = SimpleNamespace(identifier="x", resource_group=None)
    manager.add_api("x", api_without_group)
    manager.get_api("x")
    assert warnings

    with pytest.raises(AttributeError):
        manager.get_api("missing")
    assert errors

    group = SimpleNamespace(identifier="g", get_apis=lambda: {})
    manager.add_api_resource_group("g", group)
    manager.get_api_resource_group("g")
    assert manager.get_all_apis()["x"] is api_without_group
    assert manager.get_all_api_resource_groups()["g"] is group


def test_api_manager_load_all_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    manager = APIManager(auto_load_apis=False, auto_load_resource_groups=False)
    api = SimpleNamespace(identifier="api_one", resource_group=True)
    group = SimpleNamespace(identifier="group_one", get_apis=lambda: {"api_one": api})
    monkeypatch.setattr("finbot.libs.api_manager._utils.api_manager.get_all_apis", lambda: {"api_one": api})
    monkeypatch.setattr(
        "finbot.libs.api_manager._utils.api_manager.get_all_resource_groups", lambda: {"group_one": group}
    )

    manager.load_all_apis()
    manager.load_all_resource_groups()

    assert "api_one" in manager.get_all_apis()
    assert "group_one" in manager.get_all_api_resource_groups()


def test_global_api_manager_instance_exists() -> None:
    assert isinstance(global_api_manager, APIManager)


def test_logging_json_and_color_formatters() -> None:
    color = ColorFormatter("[%(asctime)s|%(name)s|", datefmt="%H:%M:%S")
    record = logging.LogRecord(
        name="finbot.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    colored = color.format(record)
    assert "hello" in colored
    assert "\033[" in colored

    formatter = LoggingJsonFormatter(rename_fields={"level": "severity"}, static_fields={"service": "finbot"})
    json_record = logging.LogRecord(
        name="finbot.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=2,
        msg="boom",
        args=(),
        exc_info=None,
    )
    json_record.trace_id = "abc123"
    payload = formatter.format(json_record)
    assert '"severity": "ERROR"' in payload
    assert '"service": "finbot"' in payload
    assert '"trace_id": "abc123"' in payload


def test_logging_filters() -> None:
    warn_record = logging.LogRecord("x", logging.WARNING, __file__, 1, "warn", (), None)
    err_record = logging.LogRecord("x", logging.ERROR, __file__, 1, "err", (), None)
    assert NonErrorFilter().filter(warn_record) is True
    assert NonErrorFilter().filter(err_record) is False
    assert ErrorFilter().filter(warn_record) is False
    assert ErrorFilter().filter(err_record) is True


def test_prepare_logging_config_contains_expected_handlers(tmp_path: Path) -> None:
    cfg = prepare_logging_config("finbot.test", "INFO", tmp_path / "finbot.test.log")
    assert cfg["version"] == 1
    assert "stdout" in cfg["handlers"]
    assert "stderr" in cfg["handlers"]
    assert "file_colored" in cfg["handlers"]
    assert "file_json" in cfg["handlers"]


def test_initialize_logger_validates_log_directory(tmp_path: Path) -> None:
    missing_dir = tmp_path / "missing"
    with pytest.raises(ValueError, match="does not exist"):
        initialize_logger("finbot.missing", "INFO", log_dir=missing_dir)


def test_initialize_logger_adds_queue_handler(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    class _DummyQueueHandler(logging.Handler):
        def emit(self, record):
            return None

    monkeypatch.setattr(
        "finbot.config.logging_config._setup_queue_logging",
        lambda *_args, **_kwargs: (_DummyQueueHandler(), object()),
    )
    test_logger = logging.getLogger("finbot.custom.logger.for.test")
    test_logger.handlers = []
    monkeypatch.setattr("finbot.config.logging_config.logging.getLogger", lambda _name=None: test_logger)
    monkeypatch.setattr(test_logger, "hasHandlers", lambda: False)

    logger = initialize_logger("finbot.custom.logger.for.test", "INFO", log_dir=log_dir)
    assert logger.handlers


def test_setup_queue_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyListener:
        def __init__(self, *_args, **_kwargs) -> None:
            self.started = False

        def start(self) -> None:
            self.started = True

        def stop(self) -> None:
            self.started = False

    base_logger = logging.getLogger("finbot.queue.test")
    base_logger.handlers = [logging.StreamHandler()]

    monkeypatch.setattr("finbot.config.logging_config.dictConfig", lambda _cfg: None)
    monkeypatch.setattr("finbot.libs.logger.setup_queue_logging.dictConfig", lambda _cfg: None)
    monkeypatch.setattr("finbot.config.logging_config.logging.getLogger", lambda _name=None: base_logger)
    monkeypatch.setattr("finbot.libs.logger.setup_queue_logging.logging.getLogger", lambda _name=None: base_logger)
    monkeypatch.setattr("finbot.config.logging_config.QueueListener", _DummyListener)
    monkeypatch.setattr("finbot.libs.logger.setup_queue_logging.QueueListener", _DummyListener)
    monkeypatch.setattr("finbot.config.logging_config.atexit.register", lambda _fn: None)
    monkeypatch.setattr("finbot.libs.logger.setup_queue_logging.atexit.register", lambda _fn: None)

    queue_handler_a, listener_a = _setup_queue_logging({"version": 1}, "finbot.queue.test")
    queue_handler_b, listener_b = setup_queue_logging({"version": 1}, "finbot.queue.test")

    assert isinstance(queue_handler_a, logging.Handler)
    assert isinstance(queue_handler_b, logging.Handler)
    assert listener_a.started is True
    assert listener_b.started is True
