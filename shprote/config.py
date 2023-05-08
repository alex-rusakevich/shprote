import toml
import os
import shutil

config = {}


def load_config(config_path="config.toml", default_config_path="default-config.toml") -> dict[any, any]:
    if not (os.path.exists(config_path) and os.path.isfile(config_path)):
        shutil.copy(default_config_path, config_path)

    config = toml.load(config_path)
    return config
