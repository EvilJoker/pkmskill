"""Tests for logging_config module"""

import os
import logging
import tempfile
import shutil
from unittest.mock import patch
import pytest


class TestSetupLogging:
    """Test setup_logging function"""

    def test_creates_log_directory(self):
        """测试创建日志目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging

            logger = setup_logging(log_dir)

            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)

    def test_creates_log_file(self):
        """测试创建日志文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging

            setup_logging(log_dir)

            log_file = os.path.join(log_dir, "pkm.log")
            assert os.path.exists(log_file)

    def test_returns_logger(self):
        """测试返回 logger 对象"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging

            logger = setup_logging(log_dir)

            assert isinstance(logger, logging.Logger)
            assert logger.level == logging.INFO

    def test_has_file_and_stream_handlers(self):
        """测试配置了文件和流处理器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging

            logger = setup_logging(log_dir)

            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "RotatingFileHandler" in handler_types
            assert "StreamHandler" in handler_types

    def test_clears_existing_handlers(self):
        """测试清除已有 handlers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging

            # 调用两次，应该清除第一次的 handlers
            setup_logging(log_dir)
            logger1 = setup_logging(log_dir)

            # handlers 数量应该正确（每个 setup 调用会先 clear 再添加）
            assert len(logger1.handlers) == 2


class TestGetLogger:
    """Test get_logger function"""

    def test_returns_logger_with_name(self):
        """测试返回指定名称的 logger"""
        from logging_config import get_logger

        logger = get_logger("test")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test"


class TestLogFormat:
    """Test log format constants"""

    def test_log_format_defined(self):
        """测试日志格式定义"""
        from logging_config import LOG_FORMAT

        assert "%(asctime)s" in LOG_FORMAT
        assert "%(name)s" in LOG_FORMAT
        assert "%(levelname)s" in LOG_FORMAT
        assert "%(message)s" in LOG_FORMAT

    def test_log_date_format_defined(self):
        """测试日期格式定义"""
        from logging_config import LOG_DATE_FORMAT

        assert "%Y" in LOG_DATE_FORMAT
        assert "%m" in LOG_DATE_FORMAT
        assert "%d" in LOG_DATE_FORMAT
        assert "%H" in LOG_DATE_FORMAT
        assert "%M" in LOG_DATE_FORMAT
        assert "%S" in LOG_DATE_FORMAT

    def test_log_dir_expands_user(self):
        """测试日志目录路径"""
        from logging_config import LOG_DIR

        assert LOG_DIR.startswith("~") or LOG_DIR.startswith("/")


class TestLogWriting:
    """Test actual log writing"""

    def test_log_message_written_to_file(self):
        """测试日志写入文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs")
            from logging_config import setup_logging, get_logger

            setup_logging(log_dir)
            logger = get_logger("test_write")
            logger.info("test message")

            # 强制写入
            for handler in logger.handlers:
                handler.flush()

            log_file = os.path.join(log_dir, "pkm.log")
            with open(log_file, "r") as f:
                content = f.read()

            assert "test message" in content
            assert "test_write" in content
