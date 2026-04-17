"""Tests for server commands (docker-compose based)"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestServerDockerComposeCommands:
    """Tests for docker-compose based server commands"""

    @patch("pathlib.Path.exists", return_value=True)
    @patch("subprocess.run")
    def test_server_start_uses_docker_compose_up(self, mock_run, mock_exists):
        """server_start 应该调用 docker compose up"""
        mock_run.return_value = MagicMock(returncode=0)

        from pkm.commands import server_cmd
        # Reload to pick up patches
        import importlib
        importlib.reload(server_cmd)

        # Mock _is_container_running to return False (not running)
        with patch.object(server_cmd, "_is_container_running", return_value=False):
            server_cmd.server_start()

        # Should call docker compose up -d
        mock_run.assert_called()
        call_str = str(mock_run.call_args_list)
        assert "compose" in call_str and "up" in call_str

    @patch("pathlib.Path.exists", return_value=True)
    @patch("subprocess.run")
    def test_server_stop_uses_docker_compose_down(self, mock_run, mock_exists):
        """server_stop 应该调用 docker compose down"""
        from pkm.commands import server_cmd
        import importlib
        importlib.reload(server_cmd)

        server_cmd.server_stop()

        mock_run.assert_called()
        call_str = str(mock_run.call_args_list)
        assert "compose" in call_str and "down" in call_str

    @patch("pathlib.Path.exists", return_value=True)
    @patch("subprocess.run")
    def test_server_status_uses_docker_compose_ps(self, mock_run, mock_exists):
        """server_status 应该调用 docker compose ps"""
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        from pkm.commands import server_cmd
        import importlib
        importlib.reload(server_cmd)

        server_cmd.server_status()

        mock_run.assert_called()
        call_str = str(mock_run.call_args_list)
        assert "compose" in call_str and "ps" in call_str

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pkm.commands.server_cmd._is_container_running", return_value=True)
    @patch("pkm.commands.server_cmd.is_server_running", return_value=True)
    @patch("subprocess.run")
    def test_server_status_shows_ready(self, mock_run, mock_svc_running, mock_container_running, mock_exists):
        """服务就绪时显示 ready"""
        from pkm.commands import server_cmd
        import importlib
        importlib.reload(server_cmd)

        server_cmd.server_status()

    @patch("pathlib.Path.exists", return_value=False)
    def test_server_start_without_compose_file(self, mock_exists):
        """docker-compose.yml 不存在时报错"""
        from pkm.commands import server_cmd
        import importlib
        importlib.reload(server_cmd)

        with patch("click.echo") as mock_echo:
            server_cmd.server_start()
            mock_echo.assert_called()
            assert "not found" in str(mock_echo.call_args).lower()
