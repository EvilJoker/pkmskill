"""install.sh installation tests - TDD style"""

import pytest
import subprocess
import os

# Mark all tests as expected failures (TDD - will pass once install.sh is fixed)
pytestmark = pytest.mark.xfail(reason="install.sh not yet fixed", strict=True)


class TestInstallScript:
    """Test install.sh installation script"""

    def test_install_script_exists(self):
        """install.sh should exist and be executable"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        assert os.path.exists(script_path), f"install.sh not found at {script_path}"
        assert os.access(script_path, os.X_OK), "install.sh should be executable"

    def test_install_script_help(self):
        """install.sh -h should show help without error"""
        result = subprocess.run(
            ["bash", "-c", "../../install.sh -h"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        assert result.returncode == 0, f"help failed: {result.stderr}"
        assert "Usage:" in result.stdout
        assert "snapshot" in result.stdout

    def test_install_script_accepts_snapshot_arg(self):
        """install.sh snapshot should attempt installation"""
        result = subprocess.run(
            ["bash", "-c", "../../install.sh snapshot"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(__file__)
        )
        output = result.stdout + result.stderr
        assert "Installing" in output or "Downloading" in output, \
            f"Expected installation output, got: {output}"

    def test_install_script_wheel_url_construction(self):
        """install.sh should construct correct wheel URL"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        with open(script_path, "r") as f:
            content = f.read()

        assert "pkm-0.0.0-py3-none-any.whl" in content, \
            "Snapshot wheel URL pattern incorrect"
        assert "releases/download" in content, \
            "Should reference GitHub releases"

    def test_install_script_docker_image_tag(self):
        """install.sh should use correct Docker image tag for snapshot"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        with open(script_path, "r") as f:
            content = f.read()

        assert "ghcr.io" in content, \
            "Should use GHCR for Docker image"
        assert ":snapshot" in content or "pkm:snapshot" in content, \
            "Snapshot should use :snapshot tag"
