import tomllib as toml

def load_config() -> dict:
    """Loads the config.toml file.

    Returns:
        dict: the config.toml file as a dict
    """
    
    with open('config.toml', 'rb') as config_file:
        return toml.load(config_file)

