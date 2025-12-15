from .config_validator import load_config

def do_something():
    config = load_config()
    # pretend to do something important with the config
    return f"Using config for user: {config.get('user', 'unknown')}"