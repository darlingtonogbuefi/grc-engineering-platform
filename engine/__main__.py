"""
Executable package entry point.

Allows:

    python -m engine
"""

from __future__ import annotations

import sys

from .exceptions import GRCError


def main() -> int:
    """
    Import and execute the main engine.

    Importing lazily avoids circular imports during startup.
    """
    try:
        from .main import main as engine_main

        return engine_main()

    except GRCError as exc:
        print(f"[GRC ERROR] {exc}")
        return 1

    except KeyboardInterrupt:
        print("\nExecution cancelled.")
        return 130

    except Exception as exc:
        print(f"[UNEXPECTED ERROR] {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
