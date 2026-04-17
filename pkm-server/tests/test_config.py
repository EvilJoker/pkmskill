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


def test_env_path_exists_branch(tmp_path, monkeypatch):
    """Test when .env already exists (skip creation branch)"""
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text("port: 7890\nlog_level: info\n")
    temp_env = temp_dir / ".env"
    temp_env.write_text("# Pre-existing env\n")

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "ENV_PATH", temp_env)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    # Call _ensure_config_files directly to test the branch
    # Since ENV_PATH exists, the else branch should execute
    pkm.config._ensure_config_files()
    # If we get here without error, the branch was covered
    assert temp_env.exists()


def test_env_path_not_exists_creates_file(tmp_path, monkeypatch):
    """Test when .env does not exist (creates file branch)"""
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text("port: 7890\nlog_level: info\n")
    temp_env = temp_dir / ".env"  # Does not exist initially

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "ENV_PATH", temp_env)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    # Call _ensure_config_files to trigger .env creation
    pkm.config._ensure_config_files()

    # Verify .env was created
    assert temp_env.exists()
    content = temp_env.read_text()
    assert "# PKM Configuration" in content


def test_config_path_exists_branch(tmp_path, monkeypatch):
    """Test when CONFIG_PATH exists (read from file branch)"""
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text("port: 9000\nlog_level: debug\n")
    temp_env = temp_dir / ".env"
    temp_env.write_text("")

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "ENV_PATH", temp_env)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    # Call load_config to test reading from existing CONFIG_PATH
    config = pkm.config.load_config()
    assert config["port"] == 9000
    assert config["log_level"] == "debug"


def test_get_api_base_with_env(monkeypatch):
    """Test get_api_base uses PKM_API_BASE env when set"""
    import pkm.config
    monkeypatch.setenv("PKM_API_BASE", "http://custom:9000")
    try:
        api_base = pkm.config.get_api_base()
        assert api_base == "http://custom:9000"
    finally:
        monkeypatch.delenv("PKM_API_BASE")


def test_get_api_base_without_env(monkeypatch, tmp_path):
    """Test get_api_base uses config when PKM_API_BASE not set"""
    import pkm.config
    temp_dir = tmp_path / ".pkm"
    temp_dir.mkdir()
    temp_config = temp_dir / "config.yaml"
    temp_config.write_text("port: 9000\nlog_level: info\n")
    temp_env = temp_dir / ".env"
    temp_env.write_text("")

    monkeypatch.setattr(pkm.config, "CONFIG_PATH", temp_config)
    monkeypatch.setattr(pkm.config, "ENV_PATH", temp_env)
    monkeypatch.setattr(pkm.config, "PKM_DIR", temp_dir)

    # Make sure PKM_API_BASE is not in env
    if "PKM_API_BASE" in os.environ:
        del os.environ["PKM_API_BASE"]

    api_base = pkm.config.get_api_base()
    assert "9000" in api_base
