from . import parser
from pathlib import Path

CONFIG = parser.parse_yaml(f"{Path(__file__).parent.parent}/config.yml")
