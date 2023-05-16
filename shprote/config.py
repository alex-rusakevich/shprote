import toml
import os
import shutil

config = {}


def load_config(config_path=os.path.join(f".", "config.toml"),
                default_config_path=os.path.join(".", "default_config.toml")) -> dict[any, any]:
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
