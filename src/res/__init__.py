# Read in yaml as dictionary
from util import parser

from pathlib import Path

STRINGS = parser.parse_yaml(f"{Path(__file__).parent}/strings.yml")
