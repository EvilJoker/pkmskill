"""PKM 日志配置模块"""
import os
import logging
from logging.handlers import RotatingFileHandler

# 日志目录
LOG_DIR = os.path.expanduser("~/.pkm/logs")

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_dir: str = LOG_DIR) -> logging.Logger:
    """
    配置双写日志：文件 + stdout

    Args:
        log_dir: 日志目录路径

    Returns:
        配置好的 logger
    """
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)

    # 获取 root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除已有的 handlers（避免重复）
    logger.handlers.clear()

    # 文件 Handler - 10MB 轮转
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "pkm.log"),
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    # stdout Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的 logger"""
    return logging.getLogger(name)
