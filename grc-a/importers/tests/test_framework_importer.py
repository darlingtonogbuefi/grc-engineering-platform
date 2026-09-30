"""
Tests for framework importer pipeline.
"""

from pathlib import Path

from importers.common.framework_importer import FrameworkImporter


def test_framework_config_exists():

    config = Path(
        "importers/configs/caf.yml"
    )

    assert config.exists()


def test_importer_initialises():

    importer = FrameworkImporter(
        "importers/configs/caf.yml"
    )

    assert importer is not None
