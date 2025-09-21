"""
生產者-消費者模式的螢幕擷取系統
使用多執行緒架構，生產者負責擷取和處理圖片，消費者負責顯示
"""

import subprocess
import time
import threading
from queue import Queue, Empty
from typing import Optional, Tuple
from dataclasses import dataclass

from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QObject, Signal, QThread, QTimer, Qt, QSize

from utils.logger import get_logger
from config.settings import (
    SCREENSHOTS_DIR, SCREENSHOT_FORMAT, SCREENSHOT_QUALITY,
    ERROR_REPORT_COOLDOWN, IMAGE_SCALE_QUALITY
)
from core.device.adb_manager import ADBManager


@dataclass
class ScreenshotData:
    """截圖數據結構"""
    pixmap: QPixmap
    timestamp: float
    resolution: Tuple[int, int]
    scaled_pixmaps: dict = None  # 預先縮放的不同尺寸版本
    
    def __post_init__(self):
        if self.scaled_pixmaps is None:
            self.scaled_pixmaps = {}


class ScreenCaptureProducer(QThread):
    """螢幕擷取生產者執行緒"""
    
    # 信號定義
    frame_ready = Signal(ScreenshotData)
    capture_error = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self, adb_manager: ADBManager, frame_queue: Queue):
        """
        初始化螢幕擷取生產者
        
        Args:
            adb_manager: ADB 管理器
            frame_queue: 圖片佇列
        """
        super().__init__()
        self.adb_manager = adb_manager
        self.frame_queue = frame_queue
        self.logger = get_logger("screen_producer")
        
        # 執行緒控制
        self.running = False
        self.capture_interval = 1.0  # 預設1秒間隔
        self.last_error_time = 0
        
        # 性能統計
        self.capture_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
        # 固定顯示尺寸（640x640 方形顯示區域）
        self.target_display_size = QSize(640, 640)
        
        # 預設縮放尺寸（保留原有的以備用）
        self.common_sizes = [
            QSize(300, 533),   # 小尺寸
            QSize(450, 800),   # 中等尺寸
            QSize(600, 1067),  # 大尺寸
            self.target_display_size,  # 固定顯示尺寸
        ]
    
    def set_capture_interval(self, interval: float):
        """
        設定擷取間隔
        
        Args:
            interval: 間隔時間（秒）
        """
        self.capture_interval = max(0.1, interval)  # 最少100ms間隔
        self.logger.info(f"擷取間隔設定為 {self.capture_interval} 秒")
    
    def start_capture(self):
        """開始擷取"""
        if not self.running:
            self.running = True
            self.start()
            self.status_changed.emit("擷取中")
            self.logger.info("螢幕擷取生產者已啟動")
    
    def stop_capture(self):
        """停止擷取"""
        if self.running:
            self.running = False
            self.status_changed.emit("已停止")
            self.logger.info("螢幕擷取生產者已停止")
    
    def run(self):
        """主執行迴圈"""
        self.logger.info("螢幕擷取生產者執行緒開始運行")
        
        while self.running:
            try:
                # 擷取螢幕
                screenshot_data = self._capture_and_process()
                
                if screenshot_data:
                    # 放入佇列（非阻塞）
                    try:
                        # 如果佇列滿了，移除舊的幀
                        while self.frame_queue.qsize() >= 3:  # 最多保留3幀
                            try:
                                self.frame_queue.get_nowait()
                            except Empty:
                                break
                        
                        self.frame_queue.put(screenshot_data, timeout=0.1)
                        self.frame_ready.emit(screenshot_data)
                        self.capture_count += 1
                        
                    except:
                        # 佇列操作失敗，但不中斷運行
                        pass
                
                # 等待下次擷取
                time.sleep(self.capture_interval)
                
            except Exception as e:
                self.logger.error(f"生產者執行緒發生錯誤: {e}")
                self.error_count += 1
                time.sleep(1.0)  # 錯誤後等待1秒
    
    def _capture_and_process(self) -> Optional[ScreenshotData]:
        """
        擷取並處理螢幕截圖
        
        Returns:
            Optional[ScreenshotData]: 處理後的截圖數據
        """
        try:
            # 檢查設備連接
            if not self.adb_manager.is_device_connected():
                self._emit_error_throttled("設備未連接")
                return None
            
            device = self.adb_manager.get_current_device()
            if not device:
                self._emit_error_throttled("無法獲取設備資訊")
                return None
            
            # 執行 ADB 截圖命令
            command = ["adb", "-s", device.address, "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                timeout=10,  # 10秒超時
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            image_data = process.stdout
            if not image_data:
                self._emit_error_throttled("無法獲取畫面數據")
                return None
            
            # 在生產者執行緒中處理圖片
            image = QImage.fromData(image_data)
            if image.isNull():
                self._emit_error_throttled("無法解析圖片數據")
                return None
            
            # 創建 QPixmap
            pixmap = QPixmap.fromImage(image)
            resolution = (image.width(), image.height())
            
            # 預先產生常用尺寸的縮放版本
            scaled_pixmaps = self._generate_scaled_versions(pixmap)
            
            # 創建截圖數據
            screenshot_data = ScreenshotData(
                pixmap=pixmap,
                timestamp=time.time(),
                resolution=resolution,
                scaled_pixmaps=scaled_pixmaps
            )
            
            return screenshot_data
            
        except subprocess.TimeoutExpired:
            self._emit_error_throttled("ADB 截圖超時")
            return None
        except FileNotFoundError:
            self._emit_error_throttled("ADB 未安裝或未在 PATH 中")
            return None
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8', errors='ignore').strip() if e.stderr else str(e)
            if "no devices/emulators found" in error_message:
                self._emit_error_throttled("未檢測到設備/模擬器")
            else:
                self._emit_error_throttled(f"ADB 命令錯誤: {error_message}")
            return None
        except Exception as e:
            self._emit_error_throttled(f"截圖處理時發生錯誤: {e}")
            return None
    
    def _generate_scaled_versions(self, pixmap: QPixmap) -> dict:
        """
        生成預先縮放的版本
        
        Args:
            pixmap: 原始圖片
            
        Returns:
            dict: 不同尺寸的縮放版本
        """
        scaled_versions = {}
        
        # 選擇變換模式
        transformation_mode = (
            Qt.TransformationMode.FastTransformation 
            if IMAGE_SCALE_QUALITY == "fast" 
            else Qt.TransformationMode.SmoothTransformation
        )
        
        for size in self.common_sizes:
            try:
                scaled_pixmap = pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    transformation_mode
                )
                scaled_versions[f"{size.width()}x{size.height()}"] = scaled_pixmap
            except Exception as e:
                self.logger.warning(f"生成縮放版本 {size} 失敗: {e}")
        
        return scaled_versions
    
    def _emit_error_throttled(self, error_msg: str):
        """
        節流的錯誤發送
        
        Args:
            error_msg: 錯誤訊息
        """
        current_time = time.time()
        if current_time - self.last_error_time > ERROR_REPORT_COOLDOWN:
            self.logger.error(error_msg)
            self.capture_error.emit(error_msg)
            self.last_error_time = current_time
    
    def get_statistics(self) -> dict:
        """
        獲取統計資訊
        
        Returns:
            dict: 統計數據
        """
        uptime = time.time() - self.start_time
        return {
            "capture_count": self.capture_count,
            "error_count": self.error_count,
            "uptime": uptime,
            "fps": self.capture_count / uptime if uptime > 0 else 0,
            "queue_size": self.frame_queue.qsize(),
            "running": self.running,
        }


class ScreenDisplayConsumer(QObject):
    """螢幕顯示消費者"""
    
    # 信號定義
    display_update = Signal(QPixmap)
    
    def __init__(self, frame_queue: Queue):
        """
        初始化螢幕顯示消費者
        
        Args:
            frame_queue: 圖片佇列
        """
        super().__init__()
        self.frame_queue = frame_queue
        self.logger = get_logger("screen_consumer")
        self.current_display_size = QSize(450, 800)  # 預設顯示尺寸
        
        # 消費者計時器
        self.consume_timer = QTimer()
        self.consume_timer.timeout.connect(self._consume_frame)
        
        # 顯示統計
        self.display_count = 0
        self.start_time = time.time()
    
    def set_display_size(self, size: QSize):
        """
        設定顯示尺寸
        
        Args:
            size: 顯示尺寸
        """
        self.current_display_size = size
        self.logger.debug(f"顯示尺寸設定為: {size.width()}x{size.height()}")
    
    def start_consuming(self, interval_ms: int = 50):
        """
        開始消費幀
        
        Args:
            interval_ms: 消費間隔（毫秒）
        """
        self.consume_timer.start(interval_ms)
        self.logger.info(f"開始消費幀，間隔: {interval_ms}ms")
    
    def stop_consuming(self):
        """停止消費"""
        self.consume_timer.stop()
        self.logger.info("停止消費幀")
    
    def _consume_frame(self):
        """消費一個幀"""
        try:
            # 非阻塞獲取最新幀
            screenshot_data = self.frame_queue.get_nowait()
            
            # 選擇最適合的縮放版本或進行實時縮放
            display_pixmap = self._get_display_pixmap(screenshot_data)
            
            if display_pixmap and not display_pixmap.isNull():
                self.display_update.emit(display_pixmap)
                self.display_count += 1
                
        except Empty:
            # 佇列為空，繼續等待
            pass
        except Exception as e:
            self.logger.warning(f"消費幀時發生錯誤: {e}")
    
    def _get_display_pixmap(self, screenshot_data: ScreenshotData) -> Optional[QPixmap]:
        """
        獲取固定尺寸的顯示 pixmap (640x640)
        
        Args:
            screenshot_data: 截圖數據
            
        Returns:
            Optional[QPixmap]: 640x640 尺寸的 pixmap
        """
        try:
            # 直接查找 640x640 的預縮放版本
            target_key = "640x640"
            
            if target_key in screenshot_data.scaled_pixmaps:
                return screenshot_data.scaled_pixmaps[target_key]
            
            # 如果沒有預先縮放的版本，實時縮放原始圖片到 640x640
            transformation_mode = (
                Qt.TransformationMode.FastTransformation 
                if IMAGE_SCALE_QUALITY == "fast" 
                else Qt.TransformationMode.SmoothTransformation
            )
            
            return screenshot_data.pixmap.scaled(
                QSize(640, 640),
                Qt.AspectRatioMode.KeepAspectRatio,
                transformation_mode
            )
            
        except Exception as e:
            self.logger.error(f"獲取固定尺寸 pixmap 失敗: {e}")
            return None
    
    def get_statistics(self) -> dict:
        """
        獲取統計資訊
        
        Returns:
            dict: 統計數據
        """
        uptime = time.time() - self.start_time
        return {
            "display_count": self.display_count,
            "uptime": uptime,
            "display_fps": self.display_count / uptime if uptime > 0 else 0,
            "queue_size": self.frame_queue.qsize(),
        }


class MultiThreadedScreenCapture(QObject):
    """多執行緒螢幕擷取系統管理器"""
    
    # 信號定義
    image_ready = Signal(QPixmap)  # 為了兼容性，與舊系統相同的信號名稱
    screenshot_saved = Signal(str)  # 截圖保存信號
    error_occurred = Signal(str)  # 錯誤信號
    status_changed = Signal(str)  # 狀態變化信號
    
    def __init__(self, adb_manager: ADBManager):
        """
        初始化多執行緒螢幕擷取系統
        
        Args:
            adb_manager: ADB 管理器
        """
        super().__init__()
        self.adb_manager = adb_manager
        self.logger = get_logger("multithreaded_screen_capture")
        
        # 建立執行緒安全的佇列
        self.frame_queue = Queue(maxsize=5)  # 最多保留5幀
        
        # 建立生產者和消費者
        self.producer = ScreenCaptureProducer(adb_manager, self.frame_queue)
        self.consumer = ScreenDisplayConsumer(self.frame_queue)
        
        # 連接信號
        self.producer.frame_ready.connect(lambda data: None)  # 生產者不需要直接發信號
        self.producer.capture_error.connect(self.error_occurred.emit)
        self.producer.status_changed.connect(self.status_changed.emit)
        self.consumer.display_update.connect(self.image_ready.emit)
    
    def start_capture(self, capture_interval: float = 1.0, display_interval_ms: int = 50):
        """
        開始擷取和顯示
        
        Args:
            capture_interval: 擷取間隔（秒）
            display_interval_ms: 顯示更新間隔（毫秒）
        """
        self.producer.set_capture_interval(capture_interval)
        self.producer.start_capture()
        self.consumer.start_consuming(display_interval_ms)
        self.logger.info("多執行緒螢幕擷取系統已啟動")
    
    def stop_capture(self):
        """停止擷取和顯示"""
        self.producer.stop_capture()
        self.consumer.stop_consuming()
        
        # 等待生產者執行緒結束
        if self.producer.isRunning():
            self.producer.wait(3000)  # 等待3秒
        
        self.logger.info("多執行緒螢幕擷取系統已停止")
    
    def set_display_size(self, size: QSize):
        """
        設定顯示尺寸
        
        Args:
            size: 顯示尺寸
        """
        self.consumer.set_display_size(size)
    
    def get_statistics(self) -> dict:
        """
        獲取系統統計資訊
        
        Returns:
            dict: 統計數據
        """
        producer_stats = self.producer.get_statistics()
        consumer_stats = self.consumer.get_statistics()
        
        return {
            "producer": producer_stats,
            "consumer": consumer_stats,
            "queue_size": self.frame_queue.qsize(),
        }
    
    def save_screenshot(self, filename: str = None):
        """
        即時截圖並保存（不依賴生產者佇列）
        
        Args:
            filename: 檔案名稱，如果為 None 則自動生成
        """
        try:
            # 直接進行即時截圖，不依賴佇列
            screenshot_data = self._capture_screenshot_immediately()
                
        except Exception as e:
            self.error_occurred.emit(f"即時截圖時發生錯誤: {e}")
            self.logger.error(f"即時截圖時發生錯誤: {e}")
        
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.{SCREENSHOT_FORMAT.lower()}"
            
        filepath = SCREENSHOTS_DIR / filename
        
        try:
            # 儲存圖片
            success = screenshot_data.pixmap.save(
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
    
    def _capture_screenshot_immediately(self) -> Optional[ScreenshotData]:
        """
        立即進行一次截圖，不依賴生產者執行緒
        
        Returns:
            Optional[ScreenshotData]: 截圖數據，如果失敗則返回 None
        """
        try:
            # 檢查設備連接
            if not self.adb_manager.is_device_connected():
                self.logger.error("設備未連接，無法進行即時截圖")
                return None
            
            device = self.adb_manager.get_current_device()
            if not device:
                self.logger.error("無法獲取設備資訊，無法進行即時截圖")
                return None
            
            # 執行 ADB 截圖命令
            command = ["adb", "-s", device.address, "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                timeout=10,  # 10秒超時
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            image_data = process.stdout
            if not image_data:
                self.logger.error("無法獲取即時截圖數據")
                return None
            
            # 處理圖片
            image = QImage.fromData(image_data)
            if image.isNull():
                self.logger.error("無法解析即時截圖數據")
                return None
            
            # 創建 QPixmap
            pixmap = QPixmap.fromImage(image)
            resolution = (image.width(), image.height())
            
            # 創建截圖數據，重用已定義的 ScreenshotData
            screenshot_data = ScreenshotData(
                pixmap=pixmap,
                timestamp=time.time(),
                resolution=resolution,
                scaled_pixmaps={}  # 即時截圖不需要預縮放版本
            )
            
            return screenshot_data
            
        except subprocess.TimeoutExpired:
            self.logger.error("即時截圖 ADB 命令超時")
            return None
        except FileNotFoundError:
            self.logger.error("ADB 未安裝或未在 PATH 中")
            return None
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8', errors='ignore').strip() if e.stderr else str(e)
            self.logger.error(f"即時截圖 ADB 命令錯誤: {error_message}")
            return None
        except Exception as e:
            self.logger.error(f"即時截圖處理時發生錯誤: {e}")
            return None
    
    def cleanup(self):
        """清理資源"""
        self.stop_capture()
        self.logger.info("多執行緒螢幕擷取系統資源已清理")