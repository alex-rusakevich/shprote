import toml
import os
import shutil
from pathlib import Path

config = {}
DATA_DIR = os.environ["SHPROTE_HOME"] or os.path.join(
    os.path.expanduser("~"), ".shprote")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


def load_config(config_path=os.path.join(f"{DATA_DIR}", "config.toml"), default_config_path="default-config.toml") -> dict[any, any]:
    if not (os.path.exists(config_path) and os.path.isfile(config_path)):
        shutil.copy(default_config_path, config_path)

    global config
    config = toml.load(config_path)
    return config


def get_config():
    global config
    if config == {}:
        load_config()
    return config
