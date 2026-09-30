# engine\main.py


"""
GRC Engineering Platform
Main Runtime Engine

Responsible for:

- Application startup
- Configuration loading
- Logging initialisation
- Runtime validation
- Engine lifecycle management

Future orchestration:

- Evidence collection
- Validation
- Mapping
- Scoring
- Reporting
"""

from __future__ import annotations

import sys

from .config import (
    RuntimeConfig,
    load_configuration,
)
from .exceptions import (
    GRCError,
)
from .logging import (
    get_logger,
    setup_logging,
)
from .version import (
    __title__,
    __version__,
)

# ==============================================================================
# Banner
# ==============================================================================


def print_banner() -> None:
    """
    Display application startup banner.
    """

    print(
        f"""
========================================
 {__title__}

 Version: {__version__}

 GRC Engineering Platform
 Compliance Automation Engine
========================================
"""
    )


# ==============================================================================
# Engine Startup
# ==============================================================================


def initialise_engine() -> RuntimeConfig:
    """
    Initialise runtime environment.

    Steps:

    1. Load configuration
    2. Validate paths
    3. Initialise directories
    4. Return runtime configuration
    """


    config = load_configuration()


    config.paths.ensure_directories()


    return config


# ==============================================================================
# Runtime Execution
# ==============================================================================


def run_engine(
    config: RuntimeConfig
) -> int:
    """
    Execute the platform.

    This will later orchestrate:

    - Collectors
    - Evidence processing
    - Framework evaluation
    - Risk scoring
    - Reporting

    """

    logger = get_logger(
        __name__
    )


    logger.info(
        "GRC engine runtime started"
    )


    if config.tenant:

        logger.info(
            "Active tenant: %s",
            config.tenant.tenant_id
        )

    else:

        logger.warning(
            "No tenant configured"
        )


    #
    # Future execution pipeline:
    #
    # 1. Collect evidence
    # 2. Validate evidence
    # 3. Map controls
    # 4. Calculate scores
    # 5. Generate reports
    #


    logger.info(
        "Engine execution completed"
    )


    return 0


# ==============================================================================
# Application Entry Point
# ==============================================================================


def main() -> int:
    """
    Main application entry point.

    Called by:

        python -m engine

    """

    try:

        print_banner()


        config = initialise_engine()


        logger = setup_logging(
            config
        )


        logger.info(
            "Configuration loaded successfully"
        )


        return run_engine(
            config
        )



    except GRCError as exc:

        print(
            f"[GRC ERROR] {exc}"
        )

        return 1



    except KeyboardInterrupt:

        print(
            "\nExecution interrupted"
        )

        return 130



    except Exception as exc:

        print(
            f"[UNEXPECTED ERROR] {exc}"
        )

        return 2


# ==============================================================================
# Direct Execution
# ==============================================================================


if __name__ == "__main__":

    sys.exit(
        main()
    )
