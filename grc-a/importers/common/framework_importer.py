"""
Framework Importer

Responsibilities

- Load configuration
- Read source document
- Build canonical model
- Write framework YAML
- Validate schemas
"""

from pathlib import Path


class FrameworkImporter:

    def __init__(self, config_file):
        self.config_file = Path(config_file)

    def load_config(self):
        raise NotImplementedError

    def read_source(self):
        raise NotImplementedError

    def build_model(self):
        raise NotImplementedError

    def write_framework(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def run(self):
        print(f"Importing using {self.config_file}")
