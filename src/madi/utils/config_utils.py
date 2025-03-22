import os
import yaml 
import logging
from pathlib import Path

from jinja2 import Template

from madi.handlers import Log


logger = Log(__name__)

assert int(os.environ.get("ENV_STAGE", 0)) in [
    0, # debug mode 
    1, # develop mode
    2, # production mode
], "ENV_STAGE must be 0, 1 or 2"

ENV_STAGE = int(
    os.environ.get("ENV_STAGE", 0)
)
CONFIG_FOLDER = (
    "dev" if (ENV_STAGE == 0 or ENV_STAGE == 1) else "prod"
)

CONFIG_PATH = Path(f"./configs/{CONFIG_FOLDER}")

logger.info("ENV_STAGE",ENV_STAGE)
logger.info("CONFIG_PATH", CONFIG_PATH)

def load_config(config_name: str) -> dict: 
    with open(CONFIG_PATH / f"{config_name}.yaml", "r") as f: 
        return yaml.safe_load(f)

def load_default_config() -> dict:
    """Loads a YAML file, renders it with Jinja2, and returns the resulting dictionary."""
    
    with open(CONFIG_PATH / "default.yaml", 'r') as file:
        config_yml = file.read()

    # Extract the CONFIG and TEMPLATE sections
    config_start = config_yml.find("---CONFIG---") + len("---CONFIG---")
    template_start = config_yml.find("---TEMPLATE---")
    
    # Extract the CONFIG section content
    config_section = config_yml[config_start:template_start].strip()
    
    # Extract the TEMPLATE section content
    template_section = config_yml[template_start + len("---TEMPLATE---"):].strip()
    
    # Load the CONFIG section as a dictionary
    config_data = yaml.safe_load(config_section)
    
    # Render the TEMPLATE section using Jinja2
    template = Template(template_section)
    rendered_template = template.render(**config_data)
    
    # Load the rendered template as a dictionary
    data = yaml.safe_load(rendered_template)
    
    return data

if __name__ == "__main__": 
    configs = load_default_config()
    print(configs)