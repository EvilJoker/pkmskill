import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pkm.config import load_config, get_port, get_log_level, CONFIG_PATH, DEFAULT_CONFIG


def test_default_config(tmp_path, monkeypatch):
    """Test default config values"""
    # Use temporary config directory to avoid环境影响
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    config = load_config()
    assert config["port"] == 7890
    assert config["log_level"] == "info"


def test_get_port(tmp_path, monkeypatch):
    """Test get_port returns correct default"""
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    assert get_port() == 7890


def test_get_log_level():
    assert get_log_level() == "info"


def test_load_config_with_file(tmp_path, monkeypatch):
    """Test loading config from a custom file"""
    # Create temporary config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text("port: 9000\nlog_level: debug\n")

    # Monkeypatch CONFIG_PATH to use temp file
    import pkm.config
    monkeypatch.setattr(pkm.config, "CONFIG_PATH", config_file)

    config = pkm.config.load_config()
    assert config["port"] == 9000
    assert config["log_level"] == "debug"


def test_load_config_partial_override(tmp_path, monkeypatch):
    """Test partial config override"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("port: 9000\n")  # Only port, no log_level

    import pkm.config
    monkeypatch.setattr(pkm.config, "CONFIG_PATH", config_file)

    config = pkm.config.load_config()
    assert config["port"] == 9000
    assert config["log_level"] == "info"  # Default


def test_config_path_default():
    """Test default config path is correct"""
    assert str(CONFIG_PATH) == str(Path("~/.pkm/config.yaml").expanduser())
