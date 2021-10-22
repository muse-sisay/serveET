from pathlib import Path
import yaml
import sys
            
def parse_yaml(f):
    with open (f, 'r') as stream :
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.exit(exc)
