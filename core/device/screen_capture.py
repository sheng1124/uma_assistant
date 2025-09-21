"""
螢幕擷取管理器
負責處理設備螢幕截圖相關功能
"""

import subprocess
import time
from typing import Optional, Tuple
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, Signal, QTimer, QThread

from utils.logger import get_logger
from config.settings import (
    SCREENSHOTS_DIR, SCREENSHOT_FORMAT, SCREENSHOT_QUALITY,
    MAX_CONCURRENT_SCREENSHOTS, ERROR_REPORT_COOLDOWN,
    IMAGE_SCALE_QUALITY
)
from core.device.adb_manager import ADBManager


class ScreenCaptureWorker(QObject):
    """螢幕擷取工作者，在背景執行緒中運行"""
    
    # 信號定義
    image_ready = Signal(QPixmap)
    capture_error = Signal(str)
    screenshot_saved = Signal(str)
    
    def __init__(self, adb_manager: ADBManager):
        """
        初始化螢幕擷取工作者
        
        Args:
            adb_manager: ADB 管理器實例
        """
        super().__init__()
        self.adb_manager = adb_manager
        self.logger = get_logger("screen_capture_worker")
        self.capturing = False
        self.last_error_time = 0
        
        # 確保截圖目錄存在
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def capture_screen_adb(self) -> bool:
        """
        使用 ADB 截取模擬器畫面（在背景執行緒中執行）
        
        Returns:
            bool: 是否成功擷取
        """
        # 防止併發擷取
        if self.capturing and MAX_CONCURRENT_SCREENSHOTS <= 1:
            return False
            
        self.capturing = True
        
        try:
            if not self.adb_manager.is_device_connected():
                self._emit_error_throttled("設備未連接")
                return False
                
            device = self.adb_manager.get_current_device()
            if not device:
                self._emit_error_throttled("無法獲取設備資訊")
                return False
                
            command = ["adb", "-s", device.address, "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                timeout=5,  # 添加超時防止卡住
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            image_data = process.stdout
            if not image_data:
                self._emit_error_throttled("無法獲取畫面數據")
                return False

            # 在背景執行緒中處理圖片
            image = QImage.fromData(image_data)
            if image.isNull():
                self._emit_error_throttled("無法解析圖片數據")
                return False
            
            # 記錄截圖資訊（僅 debug 模式）
            self.logger.debug(f"截圖成功，解析度: {image.width()}x{image.height()}")

            pixmap = QPixmap.fromImage(image)
            self.image_ready.emit(pixmap)
            return True

        except subprocess.TimeoutExpired:
            self._emit_error_throttled("ADB 截圖超時")
            return False
        except FileNotFoundError:
            self._emit_error_throttled("ADB 未安裝或未在 PATH 中")
            return False
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8', errors='ignore').strip() if e.stderr else str(e)
            if "no devices/emulators found" in error_message:
                self._emit_error_throttled("未檢測到設備/模擬器")
            else:
                self._emit_error_throttled(f"ADB 命令錯誤: {error_message}")
            return False
        except Exception as e:
            self._emit_error_throttled(f"截圖時發生未知錯誤: {e}")
            return False
        finally:
            self.capturing = False
    
    def _emit_error_throttled(self, error_msg: str):
        """
        節流的錯誤發送，避免錯誤訊息洪水
        
        Args:
            error_msg: 錯誤訊息
        """
        current_time = time.time()
        if current_time - self.last_error_time > ERROR_REPORT_COOLDOWN:
            self.logger.error(error_msg)
            self.capture_error.emit(error_msg)
            self.last_error_time = current_time


class ScreenCapture(QObject):
    """螢幕擷取管理器"""
    
    # 信號定義
    image_ready = Signal(QPixmap)
    capture_error = Signal(str)
    screenshot_saved = Signal(str)
    
    def __init__(self, adb_manager: ADBManager):
        """
        初始化螢幕擷取管理器
        
        Args:
            adb_manager: ADB 管理器實例
        """
        super().__init__()
        self.adb_manager = adb_manager
        self.logger = get_logger("screen_capture")
        
        # 創建背景執行緒和工作者
        self.worker_thread = QThread()
        self.worker = ScreenCaptureWorker(adb_manager)
        self.worker.moveToThread(self.worker_thread)
        
        # 連接信號
        self.worker.image_ready.connect(self.image_ready.emit)
        self.worker.capture_error.connect(self.capture_error.emit)
        self.worker.screenshot_saved.connect(self.screenshot_saved.emit)
        
        # 啟動工作執行緒
        self.worker_thread.start()
    
    def capture_screen_adb(self) -> None:
        """
        請求螢幕擷取（非阻塞）
        """
        # 使用 QTimer.singleShot 在背景執行緒中執行
        QTimer.singleShot(0, self.worker.capture_screen_adb)
    
    def save_screenshot_to_file(self, filename: Optional[str] = None) -> bool:
        """
        截取畫面並儲存為檔案
        
        Args:
            filename: 檔案名稱，若未提供則自動生成
            
        Returns:
            bool: 儲存是否成功
        """
        pixmap = self.capture_screen_adb()
        if pixmap is None:
            return False
            
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.{SCREENSHOT_FORMAT.lower()}"
            
        filepath = SCREENSHOTS_DIR / filename
        
        try:
            # 儲存圖片
            success = pixmap.save(
                str(filepath),
                SCREENSHOT_FORMAT,
                SCREENSHOT_QUALITY
            )
            
            if success:
                message = f"螢幕截圖已儲存至 {filepath}"
                self.logger.info(message)
                self.screenshot_saved.emit(message)
                return True
            else:
                error_msg = "儲存截圖檔案失敗"
                self.logger.error(error_msg)
                self.capture_error.emit(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"儲存截圖時發生錯誤: {e}"
            self.logger.error(error_msg)
            self.capture_error.emit(error_msg)
            return False
    
    def get_screen_size(self) -> Optional[Tuple[int, int]]:
        """
        獲取螢幕尺寸
        
        Returns:
            Optional[Tuple[int, int]]: (寬度, 高度)，失敗時返回 None
        """
        pixmap = self.capture_screen_adb()
        if pixmap:
            return pixmap.width(), pixmap.height()
        return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[QPixmap]:
        """
        截取螢幕指定區域
        
        Args:
            x: 起始 x 座標
            y: 起始 y 座標
            width: 寬度
            height: 高度
            
        Returns:
            Optional[QPixmap]: 區域截圖，失敗時返回 None
        """
        full_screen = self.capture_screen_adb()
        if full_screen is None:
            return None
            
        # 檢查座標是否有效
        if (x < 0 or y < 0 or x + width > full_screen.width() or 
            y + height > full_screen.height()):
            error_msg = f"無效的截取區域: ({x}, {y}, {width}, {height})"
            self.logger.error(error_msg)
            self.capture_error.emit(error_msg)
            return None
            
        # 截取指定區域
        region_pixmap = full_screen.copy(x, y, width, height)
        return region_pixmap