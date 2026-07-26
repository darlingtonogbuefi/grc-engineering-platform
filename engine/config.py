"""
GRC Engineering Platform
Configuration Management

Responsible for:

- Environment loading
- Runtime paths
- Configuration models
- Tenant-aware configuration foundation

The configuration system supports:

- CAF
- ISO27001
- SOC2
- GovAssure
- Cyber Essentials

Configuration sources:

1. Environment variables (.env)
2. config/*.yml files
3. Runtime overrides
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .exceptions import ConfigurationError

# ==============================================================================
# Environment Initialisation
# ==============================================================================


PROJECT_ROOT = Path(__file__).resolve().parent.parent


ENV_FILE = PROJECT_ROOT / ".env"


if ENV_FILE.exists():
    load_dotenv(ENV_FILE)



# ==============================================================================
# Helper Functions
# ==============================================================================


def get_env(
    name: str,
    default: str = ""
) -> str:
    """
    Retrieve environment variable.

    Always returns a string.
    Environment variables take precedence over defaults.
    """

    value = os.getenv(name)

    if value is None:
        return default

    return value



def get_bool_env(
    name: str,
    default: bool = False
) -> bool:
    """
    Convert environment variable into boolean.
    """

    value = os.getenv(name)


    if value is None:
        return default


    return value.lower() in (
        "true",
        "1",
        "yes",
        "y",
        "on"
    )



# ==============================================================================
# Path Configuration
# ==============================================================================


@dataclass(frozen=True)
class PathConfig:
    """
    Application filesystem paths.
    """


    root: Path = PROJECT_ROOT


    config: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "config"
    )


    frameworks: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "frameworks"
    )


    capabilities: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "capabilities"
    )


    collectors: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "collectors"
    )


    schemas: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "schemas"
    )


    evidence: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "evidence"
    )


    reports: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "reports"
    )


    output: Path = field(
        default_factory=lambda:
        PROJECT_ROOT / "output"
    )


    def ensure_directories(self) -> None:
        """
        Ensure runtime directories exist.
        """

        directories = [

            self.evidence,

            self.reports,

            self.output

        ]


        for directory in directories:

            directory.mkdir(
                parents=True,
                exist_ok=True
            )



# ==============================================================================
# Application Configuration
# ==============================================================================


@dataclass
class ApplicationConfig:
    """
    General application configuration.
    """


    name: str = field(
        default_factory=lambda:
        get_env(
            "APP_NAME",
            "grc-engineering-platform"
        )
    )


    environment: str = field(
        default_factory=lambda:
        get_env(
            "APP_ENV",
            "development"
        )
    )


    version: str = field(
        default_factory=lambda:
        get_env(
            "APP_VERSION",
            "0.1.0"
        )
    )


    log_level: str = field(
        default_factory=lambda:
        get_env(
            "LOG_LEVEL",
            "INFO"
        )
    )


    timezone: str = field(
        default_factory=lambda:
        get_env(
            "TIMEZONE",
            "Europe/London"
        )
    )



# ==============================================================================
# Storage Configuration
# ==============================================================================


@dataclass
class StorageConfig:
    """
    Evidence storage configuration.
    """


    provider: str = field(
        default_factory=lambda:
        get_env(
            "STORAGE_PROVIDER",
            "local"
        )
    )


    encryption_enabled: bool = field(
        default_factory=lambda:
        get_bool_env(
            "STORAGE_ENCRYPTION",
            True
        )
    )


    local_path: Path = field(
        default_factory=lambda:
        Path(
            get_env(
                "LOCAL_STORAGE_PATH",
                "./data"
            )
        )
    )



# ==============================================================================
# Tenant Configuration
# ==============================================================================


@dataclass
class TenantContext:
    """
    Active tenant runtime context.
    """


    tenant_id: str


    frameworks: list[str] = field(
        default_factory=list
    )


    collectors: list[str] = field(
        default_factory=list
    )


    metadata: dict[str, Any] = field(
        default_factory=dict
    )



# ==============================================================================
# Complete Runtime Configuration
# ==============================================================================


@dataclass
class RuntimeConfig:
    """
    Complete runtime configuration object.
    """


    paths: PathConfig = field(
        default_factory=PathConfig
    )


    application: ApplicationConfig = field(
        default_factory=ApplicationConfig
    )


    storage: StorageConfig = field(
        default_factory=StorageConfig
    )


    tenant: TenantContext | None = None



    def validate(self) -> None:
        """
        Basic runtime validation.
        """


        if not self.paths.config.exists():

            raise ConfigurationError(
                f"Missing configuration directory: "
                f"{self.paths.config}"
            )


        if not self.paths.schemas.exists():

            raise ConfigurationError(
                f"Missing schemas directory: "
                f"{self.paths.schemas}"
            )



# ==============================================================================
# YAML Configuration Loading
# ==============================================================================

import yaml


def load_yaml_file(
    path: Path
) -> dict[str, Any]:
    """
    Load YAML configuration file.

    Args:
        path:
            YAML file location

    Returns:
        Parsed YAML dictionary
    """

    if not path.exists():

        raise ConfigurationError(
            f"Configuration file not found: {path}"
        )


    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = yaml.safe_load(file)


            if data is None:

                return {}


            if not isinstance(
                data,
                dict
            ):

                raise ConfigurationError(
                    f"Invalid YAML structure: {path}"
                )


            return data


    except yaml.YAMLError as exc:

        raise ConfigurationError(
            f"Unable to parse YAML file {path}: {exc}"
        ) from exc



# ==============================================================================
# Configuration Repository
# ==============================================================================


@dataclass
class ConfigurationRepository:
    """
    Stores loaded YAML configuration objects.
    """


    tenants: dict[str, Any] = field(
        default_factory=dict
    )


    frameworks: dict[str, Any] = field(
        default_factory=dict
    )


    collectors: dict[str, Any] = field(
        default_factory=dict
    )


    reporting: dict[str, Any] = field(
        default_factory=dict
    )


    storage: dict[str, Any] = field(
        default_factory=dict
    )



# ==============================================================================
# YAML Configuration Loader
# ==============================================================================


class ConfigLoader:
    """
    Loads platform configuration.

    Responsible for:

    - YAML parsing
    - Configuration discovery
    - Tenant loading
    - Framework loading
    - Collector loading
    """


    def __init__(
        self,
        paths: PathConfig | None = None
    ) -> None:


        self.paths = paths or PathConfig()

        self.repository = ConfigurationRepository()



    def load(
        self
    ) -> ConfigurationRepository:
        """
        Load all configuration files.
        """


        self.repository.tenants = (
            self.load_config(
                "tenants.yml"
            )
        )


        self.repository.frameworks = (
            self.load_config(
                "frameworks.yml"
            )
        )


        self.repository.collectors = (
            self.load_config(
                "collectors.yml"
            )
        )


        self.repository.reporting = (
            self.load_config(
                "reporting.yml"
            )
        )


        self.repository.storage = (
            self.load_config(
                "storage.yml"
            )
        )


        return self.repository



    def load_config(
        self,
        filename: str
    ) -> dict[str, Any]:
        """
        Load configuration file from config directory.
        """


        config_file = (
            self.paths.config / filename
        )


        return load_yaml_file(
            config_file
        )



# ==============================================================================
# Tenant Loader
# ==============================================================================


class TenantLoader:
    """
    Loads tenant configuration.
    """


    def __init__(
        self,
        repository: ConfigurationRepository
    ) -> None:

        self.repository = repository



    def get_tenant(
        self,
        tenant_id: str
    ) -> TenantContext:
        """
        Retrieve tenant runtime context.
        """


        tenants = (
            self.repository.tenants
        )


        tenant = tenants.get(
            tenant_id
        )


        if tenant is None:

            raise ConfigurationError(
                f"Tenant not found: {tenant_id}"
            )


        return TenantContext(

            tenant_id=tenant_id,

            frameworks=tenant.get(
                "frameworks",
                []
            ),

            collectors=tenant.get(
                "collectors",
                []
            ),

            metadata=tenant

        )



# ==============================================================================
# Framework Loader
# ==============================================================================


class FrameworkLoader:
    """
    Provides framework definitions.
    """


    def __init__(
        self,
        repository: ConfigurationRepository
    ) -> None:

        self.repository = repository



    def list_frameworks(
        self
    ) -> list[str]:
        """
        Return configured frameworks.
        """


        frameworks = (
            self.repository.frameworks
        )


        return list(
            frameworks.keys()
        )



    def get_framework(
        self,
        framework_id: str
    ) -> dict[str, Any]:
        """
        Return framework configuration.
        """


        framework = (
            self.repository.frameworks.get(
                framework_id
            )
        )


        if framework is None:

            raise ConfigurationError(
                f"Framework not found: {framework_id}"
            )


        return framework



# ==============================================================================
# Collector Loader
# ==============================================================================


class CollectorLoader:
    """
    Provides collector definitions.
    """


    def __init__(
        self,
        repository: ConfigurationRepository
    ) -> None:

        self.repository = repository



    def list_collectors(
        self
    ) -> list[str]:

        return list(
            self.repository.collectors.keys()
        )



    def get_collector(
        self,
        collector_id: str
    ) -> dict[str, Any]:
        """
        Return collector configuration.
        """


        collector = (
            self.repository.collectors.get(
                collector_id
            )
        )


        if collector is None:

            raise ConfigurationError(
                f"Collector not found: {collector_id}"
            )


        return collector



# ==============================================================================
# Public API
# ==============================================================================


def load_configuration() -> RuntimeConfig:
    """
    Public configuration loader.

    Example:

        config = load_configuration()

        print(config.tenant)

    """


    paths = PathConfig()


    paths.ensure_directories()


    repository = ConfigLoader(
        paths
    ).load()



    tenant_id: str = get_env(
    "DEFAULT_TENANT",
    "demo"
    )


    tenant = None


    if tenant_id in repository.tenants:

        tenant = TenantLoader(
            repository
        ).get_tenant(
            tenant_id
        )



    runtime = RuntimeConfig(

        paths=paths,

        tenant=tenant

    )


    runtime.validate()


    return runtime
