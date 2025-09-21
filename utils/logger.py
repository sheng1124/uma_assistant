"""
日誌系統工具
提供統一的日誌記錄功能
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config.settings import (
    LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT,
    LOG_MAX_BYTES, LOG_BACKUP_COUNT
)


def get_logger(name: str) -> logging.Logger:
    """
    獲取指定名稱的日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        
    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # 設定日誌級別
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
        
        # 創建格式化器
        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT
        )
        
        # 創建並配置檔案處理器（輪轉）
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 創建並配置控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 防止重複記錄
        logger.propagate = False
    
    return logger


def setup_root_logger():
    """設定根日誌記錄器"""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # 確保日誌檔案目錄存在
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


class LogContext:
    """日誌上下文管理器，用於臨時改變日誌級別"""
    
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


# 在模組載入時設定根日誌記錄器
setup_root_logger()