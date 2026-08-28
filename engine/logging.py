# engine\logging.py

"""
GRC Engineering Platform
Logging Management

Central logging configuration.

Provides:

- Application logging
- Collector execution logs
- Evidence collection traceability
- Structured logging support
- File rotation
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import RuntimeConfig

# ==============================================================================
# Constants
# ==============================================================================


DEFAULT_LOG_FORMAT = "%(asctime)s " "| %(levelname)s " "| %(name)s " "| %(message)s"


DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


LOG_DIRECTORY_NAME = "logs"


# ==============================================================================
# JSON Formatter
# ==============================================================================


class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON.

    Useful for:

    - SIEM ingestion
    - Azure Monitor
    - Splunk
    - Elastic
    """

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        """
        Convert a logging record into a JSON document.
        """

        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=UTC,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        tenant_id = getattr(
            record,
            "tenant_id",
            None,
        )

        if tenant_id is not None:
            payload["tenant_id"] = tenant_id

        collector = getattr(
            record,
            "collector",
            None,
        )

        if collector is not None:
            payload["collector"] = collector

        evidence_id = getattr(
            record,
            "evidence_id",
            None,
        )

        if evidence_id is not None:
            payload["evidence_id"] = evidence_id

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info,
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


# ==============================================================================
# Logging Context Adapter
# ==============================================================================


class GRCLoggerAdapter(
    logging.LoggerAdapter,
):
    """
    Adds GRC-specific context fields.

    Example:

        logger.info(
            "Collection started",
            extra={
                "collector": "entra"
            }
        )

    The adapter can also carry persistent context:

        logger = GRCLoggerAdapter(
            get_logger(__name__),
            {
                "tenant_id": "tenant-001",
                "collector": "azure",
            },
        )

        logger.info("Collection started")
    """

    def process(
        self,
        msg: Any,
        kwargs: dict[str, Any],
    ) -> tuple[Any, dict[str, Any]]:
        """
        Merge adapter context into the logging ``extra`` dictionary.
        """

        extra = kwargs.setdefault(
            "extra",
            {},
        )

        extra.update(
            self.extra,
        )

        return msg, kwargs


# ==============================================================================
# Log Level Helper
# ==============================================================================


def get_log_level(
    level: str,
) -> int:
    """
    Convert string log level into logging constant.
    """

    level = level.upper()

    return getattr(
        logging,
        level,
        logging.INFO,
    )


# ==============================================================================
# Logging Setup
# ==============================================================================


def setup_logging(
    config: RuntimeConfig,
) -> logging.Logger:
    """
    Configure application logging.

    Creates:

    - Console handler
    - Rotating file handler

    Returns:

        Root application logger
    """

    log_level = get_log_level(
        config.application.log_level,
    )

    logger = logging.getLogger(
        "grc-engineering-platform",
    )

    logger.setLevel(
        log_level,
    )

    logger.handlers.clear()

    formatter = logging.Formatter(
        DEFAULT_LOG_FORMAT,
        DEFAULT_DATE_FORMAT,
    )

    # --------------------------------------------------------------------------
    # Console Handler
    # --------------------------------------------------------------------------

    console_handler = logging.StreamHandler(
        sys.stdout,
    )

    console_handler.setLevel(
        log_level,
    )

    console_handler.setFormatter(
        formatter,
    )

    logger.addHandler(
        console_handler,
    )

    # --------------------------------------------------------------------------
    # File Handler
    # --------------------------------------------------------------------------

    log_directory = config.paths.output / LOG_DIRECTORY_NAME

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = log_directory / "grc-engineering-platform.log"

    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10_485_760,
        backupCount=10,
        encoding="utf-8",
    )

    file_handler.setLevel(
        log_level,
    )

    file_handler.setFormatter(
        formatter,
    )

    logger.addHandler(
        file_handler,
    )

    logger.info(
        "Logging initialised",
    )

    return logger


# ==============================================================================
# JSON Logging Setup
# ==============================================================================


def enable_json_logging(
    logger: logging.Logger,
    log_file: Path,
) -> None:
    """
    Add JSON log output.

    Used for:

    - SIEM ingestion
    - Compliance monitoring
    - Audit trails
    """

    handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10_485_760,
        backupCount=10,
        encoding="utf-8",
    )

    handler.setFormatter(
        JsonFormatter(),
    )

    logger.addHandler(
        handler,
    )


# ==============================================================================
# Child Logger Factory
# ==============================================================================


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Retrieve module logger.

    Example:

        logger = get_logger(__name__)
    """

    return logging.getLogger(
        f"grc-engineering-platform.{name}",
    )


# ==============================================================================
# Audit Logging Helpers
# ==============================================================================


def log_collector_event(
    logger: logging.Logger,
    collector: str,
    message: str,
    tenant_id: str | None = None,
) -> None:
    """
    Log collector activity.

    Used by collectors for:

    - Start
    - Completion
    - Failure
    - Evidence counts
    """

    extra: dict[str, Any] = {
        "collector": collector,
    }

    if tenant_id:
        extra["tenant_id"] = tenant_id

    logger.info(
        message,
        extra=extra,
    )


def log_evidence_event(
    logger: logging.Logger,
    evidence_id: str,
    message: str,
    tenant_id: str | None = None,
) -> None:
    """
    Log evidence lifecycle events.
    """

    extra: dict[str, Any] = {
        "evidence_id": evidence_id,
    }

    if tenant_id:
        extra["tenant_id"] = tenant_id

    logger.info(
        message,
        extra=extra,
    )
