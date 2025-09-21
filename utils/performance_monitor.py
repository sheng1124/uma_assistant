"""
性能監控工具
用於監控應用程式的性能指標
"""

import time
import psutil
import threading
from typing import Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer

from utils.logger import get_logger


class PerformanceMonitor(QObject):
    """性能監控器"""
    
    # 信號定義
    performance_update = Signal(dict)  # 性能數據更新
    
    def __init__(self):
        """初始化性能監控器"""
        super().__init__()
        self.logger = get_logger("performance_monitor")
        self.monitoring = False
        self.process = psutil.Process()
        
        # 統計數據
        self.stats = {
            "screenshot_count": 0,
            "screenshot_errors": 0,
            "ui_updates": 0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "start_time": time.time(),
        }
        
        # 定時器
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._collect_metrics)
        
    def start_monitoring(self, interval_ms: int = 2000):
        """
        開始監控
        
        Args:
            interval_ms: 監控間隔（毫秒）
        """
        self.monitoring = True
        self.stats["start_time"] = time.time()
        self.monitor_timer.start(interval_ms)
        self.logger.info("性能監控已開始")
    
    def stop_monitoring(self):
        """停止監控"""
        self.monitoring = False
        self.monitor_timer.stop()
        self.logger.info("性能監控已停止")
    
    def record_screenshot(self, success: bool):
        """
        記錄截圖事件
        
        Args:
            success: 截圖是否成功
        """
        if success:
            self.stats["screenshot_count"] += 1
        else:
            self.stats["screenshot_errors"] += 1
    
    def record_ui_update(self):
        """記錄 UI 更新事件"""
        self.stats["ui_updates"] += 1
    
    def _collect_metrics(self):
        """收集性能指標"""
        try:
            # 記憶體使用量（MB）
            memory_info = self.process.memory_info()
            self.stats["memory_usage"] = memory_info.rss / 1024 / 1024
            
            # CPU 使用率
            self.stats["cpu_usage"] = self.process.cpu_percent()
            
            # 運行時間
            self.stats["uptime"] = time.time() - self.stats["start_time"]
            
            # 計算速率
            uptime_minutes = self.stats["uptime"] / 60
            if uptime_minutes > 0:
                self.stats["screenshot_rate"] = self.stats["screenshot_count"] / uptime_minutes
                self.stats["error_rate"] = self.stats["screenshot_errors"] / uptime_minutes
                self.stats["ui_update_rate"] = self.stats["ui_updates"] / uptime_minutes
            
            # 發送更新信號
            self.performance_update.emit(self.stats.copy())
            
        except Exception as e:
            self.logger.error(f"收集性能指標時發生錯誤: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """
        獲取當前統計數據
        
        Returns:
            Dict[str, Any]: 統計數據
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置統計數據"""
        self.stats.update({
            "screenshot_count": 0,
            "screenshot_errors": 0,
            "ui_updates": 0,
            "start_time": time.time(),
        })