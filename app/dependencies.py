import toml

def load_config() -> dict:
    """Loads the config.toml file.

    Returns:
        dict: the config.toml file as a dict
    """
    return toml.load("config.toml")
