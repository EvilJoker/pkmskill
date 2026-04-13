"""install.sh installation tests - TDD style"""

import pytest
import subprocess
import os
import re

# Snapshot 安装目标：
# 1. 从 GitHub releases 下载最新的 whl 包
# 2. 下载 ghcr.io/eviljoker/pkm:snapshot Docker 镜像


class TestInstallSnapshot:
    """Test install.sh snapshot command - end-to-end TDD"""

    def test_snapshot_help(self):
        """install.sh snapshot -h should show help"""
        result = subprocess.run(
            ["bash", "-c", "../install.sh snapshot -h"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        assert result.returncode == 0, f"help failed: {result.stderr}"
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()

    def test_snapshot_downloads_wheel(self):
        """install.sh snapshot should download wheel from GitHub releases"""
        result = subprocess.run(
            ["bash", "-c", "../install.sh snapshot 2>&1"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=os.path.dirname(__file__)
        )
        output = result.stdout + result.stderr

        # 应该显示正在下载 whl
        assert "whl" in output.lower() or "wheel" in output.lower() or "downloading" in output.lower(), \
            f"Expected wheel download output, got: {output}"

    def test_snapshot_downloads_docker_image(self):
        """install.sh snapshot should pull Docker image"""
        result = subprocess.run(
            ["bash", "-c", "../install.sh snapshot 2>&1"],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=os.path.dirname(__file__)
        )
        output = result.stdout + result.stderr

        # 应该显示正在下载 Docker 镜像
        assert "docker" in output.lower() or "image" in output.lower() or "pulling" in output.lower(), \
            f"Expected Docker image download output, got: {output}"

    def test_snapshot_uses_correct_image_tag(self):
        """install.sh should use ghcr.io/eviljoker/pkm:snapshot tag"""
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "install.sh")
        with open(script_path, "r") as f:
            content = f.read()

        assert "ghcr.io/eviljoker/pkm:snapshot" in content or "eviljoker/pkm.*snapshot" in content, \
            f"Should use ghcr.io/eviljoker/pkm:snapshot, got: {content[:500]}"

    def test_snapshot_extracts_version_from_github(self):
        """install.sh should get latest version from GitHub API"""
        script_path = os.path.join(os.path.dirname(__file__), "..", "..", "install.sh")
        with open(script_path, "r") as f:
            content = f.read()

        # 应该使用 GitHub API 获取最新版本
        assert "api.github.com" in content or "github.com/api" in content, \
            f"Should use GitHub API for latest release, got: {content[:500]}"
        assert "releases/latest" in content or "releases" in content, \
            f"Should fetch latest release, got: {content[:500]}"

    def test_snapshot_completes_successfully(self):
        """install.sh snapshot should complete without error"""
        result = subprocess.run(
            ["bash", "-c", "../install.sh snapshot 2>&1"],
            capture_output,
            text=True,
            timeout=180,
            cwd=os.path.dirname(__file__)
        )
        output = result.stdout + result.stderr

        # 退出码应该是 0（成功）或者输出包含完成信息
        assert result.returncode == 0, f"install.sh snapshot failed with: {output}"
