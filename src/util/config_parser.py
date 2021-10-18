from pathlib import Path
import yaml
import sys

def read_config ():
    with open(f"{Path(__file__).parent.parent}/config.yml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.exit(exc)
            

CONFIG = read_config()
