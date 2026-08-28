# engine\version.py

"""
Version information.
"""

__title__ = "grc-engineering-platform"

__version__ = "0.1.0"

__author__ = "GRC Engineering Platform Team"

__license__ = "Apache-2.0"


# ==============================================================================
# Supported Frameworks
# ==============================================================================

SUPPORTED_FRAMEWORKS = (
    "NCSC_CAF",
    "ISO_42001",
    "ISO_27001",
    "SOC_2",
    "CYBER_ESSENTIALS",
    "GOV_ASSURANCE",
)


# ==============================================================================
# Supported Collectors
# ==============================================================================

SUPPORTED_COLLECTORS = (
    "entra",
    "azure",
    "intune",
    "defender",
    "exchange",
    "teams",
    "sharepoint",
    "onedrive",
    "purview",
    "github",
    "azuredevops",
    "powerplatform",
    "dynamics365",
    "azurearc",
    "vmware",
)
