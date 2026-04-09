import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "port": 7890,
    "log_level": "info",
}

PKM_DIR = Path("~/.pkm").expanduser()
CONFIG_PATH = PKM_DIR / "config.yaml"
ENV_PATH = PKM_DIR / ".env"


def _ensure_config_files():
    """Ensure default config files exist in ~/.pkm/"""
    PKM_DIR.mkdir(parents=True, exist_ok=True)

    # Create config.yaml if not exists
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f)

    # Create .env if not exists (empty template)
    if not ENV_PATH.exists():
        with open(ENV_PATH, "w") as f:
            f.write("# PKM Configuration\n")
            f.write("# API_KEY=your-api-key-here\n")


def load_config() -> dict:
    """Load config from ~/.pkm/config.yaml, fallback to defaults"""
    _ensure_config_files()
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    return config


def get_port() -> int:
    return load_config()["port"]


def get_log_level() -> str:
    return load_config()["log_level"]
