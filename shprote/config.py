import toml
import os
import shutil

config = {}


def load_config(config_path=os.path.join(f".", "config.toml"),
                default_config_path=os.path.join(".", "default_config.toml")) -> dict[any, any]:
    global config
    if os.environ.get("DYNO"):
        config = toml.load(default_config_path)
        return config

    if not (os.path.exists(config_path) and os.path.isfile(config_path)):
        shutil.copy(default_config_path, config_path)
    config = toml.load(config_path)
    return config


def get_config():
    global config
    if config == {}:
        load_config()
    return config


def save_config(config_path=os.path.join(f".", "config.toml")):
    global config
    with open(config_path, 'w', encoding='utf8') as f:
        toml.dump(config, f)
