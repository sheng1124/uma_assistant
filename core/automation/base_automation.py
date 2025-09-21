"""
自動化基底類別
定義所有自動化腳本的共用介面和基礎功能
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum

from config.settings import AUTOMATION_INTERVALS
from utils.logger import get_logger


class AutomationState(Enum):
    """自動化狀態枚舉"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class BaseAutomation(ABC):
    """自動化基底類別"""
    
    def __init__(self, name: str):
        """
        初始化自動化實例
        
        Args:
            name: 自動化腳本名稱
        """
        self.name = name
        self.state = AutomationState.STOPPED
        self.logger = get_logger(f"automation.{name}")
        self.config = {}
        self.running = False
        self.paused = False
        
    @abstractmethod
    def setup(self, config: Dict[str, Any]) -> bool:
        """
        設定自動化腳本
        
        Args:
            config: 配置參數
            
        Returns:
            bool: 設定是否成功
        """
        pass
    
    @abstractmethod
    def execute_step(self) -> bool:
        """
        執行單一自動化步驟
        
        Returns:
            bool: 步驟是否成功執行
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理資源"""
        pass
    
    def start(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        開始執行自動化腳本
        
        Args:
            config: 可選的配置參數
            
        Returns:
            bool: 啟動是否成功
        """
        if self.state == AutomationState.RUNNING:
            self.logger.warning(f"{self.name} 已在執行中")
            return False
            
        if config:
            self.config.update(config)
            
        if not self.setup(self.config):
            self.logger.error(f"{self.name} 設定失敗")
            self.state = AutomationState.ERROR
            return False
            
        self.running = True
        self.paused = False
        self.state = AutomationState.RUNNING
        self.logger.info(f"{self.name} 開始執行")
        return True
    
    def stop(self):
        """停止執行自動化腳本"""
        self.running = False
        self.paused = False
        self.state = AutomationState.STOPPED
        self.cleanup()
        self.logger.info(f"{self.name} 已停止")
    
    def pause(self):
        """暫停執行自動化腳本"""
        if self.state == AutomationState.RUNNING:
            self.paused = True
            self.state = AutomationState.PAUSED
            self.logger.info(f"{self.name} 已暫停")
    
    def resume(self):
        """恢復執行自動化腳本"""
        if self.state == AutomationState.PAUSED:
            self.paused = False
            self.state = AutomationState.RUNNING
            self.logger.info(f"{self.name} 已恢復執行")
    
    def run_loop(self):
        """主執行迴圈"""
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
                
            try:
                if not self.execute_step():
                    self.logger.error(f"{self.name} 執行步驟失敗")
                    self.state = AutomationState.ERROR
                    break
                    
                # 執行間隔
                time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
                
            except Exception as e:
                self.logger.error(f"{self.name} 執行過程中發生錯誤: {e}")
                self.state = AutomationState.ERROR
                break
        
        if self.state != AutomationState.STOPPED:
            self.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取當前狀態資訊
        
        Returns:
            Dict: 狀態資訊
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "running": self.running,
            "paused": self.paused,
            "config": self.config.copy()
        }
    
    def wait_for_condition(self, condition_func, timeout: float = 10.0, interval: float = 0.5) -> bool:
        """
        等待條件滿足
        
        Args:
            condition_func: 條件檢查函數
            timeout: 超時時間（秒）
            interval: 檢查間隔（秒）
            
        Returns:
            bool: 條件是否在超時前滿足
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False