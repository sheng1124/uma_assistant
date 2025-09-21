"""
螢幕顯示元件
顯示設備螢幕擷取畫面
"""

from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from config.ui_config import SCREEN_DISPLAY
from config.settings import UI_UPDATE_THROTTLE, IMAGE_SCALE_QUALITY
from core.device.multithreaded_screen_capture import MultiThreadedScreenCapture
from utils.logger import get_logger


class FixedSizeScreenLabel(QLabel):
    """固定尺寸的螢幕顯示標籤"""
    
    def __init__(self, fixed_width=640, fixed_height=640, parent=None):
        """
        初始化固定尺寸標籤
        
        Args:
            fixed_width: 固定寬度
            fixed_height: 固定高度
            parent: 父元件
        """
        super().__init__(parent)
        self.fixed_width = fixed_width
        self.fixed_height = fixed_height
        
        # 設定固定尺寸
        self.setFixedSize(fixed_width, fixed_height)
        self.setScaledContents(False)  # 不自動縮放內容
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def set_fixed_pixmap(self, pixmap: QPixmap):
        """
        設定已經處理好的固定尺寸 pixmap
        
        Args:
            pixmap: 已經縮放到固定尺寸的 pixmap
        """
        if pixmap and not pixmap.isNull():
            self.setPixmap(pixmap)


class OptimizedScreenLabel(QLabel):
    """優化的螢幕顯示標籤"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cached_size = None
        self.cached_pixmap = None
        self.original_pixmap = None
    
    def set_optimized_pixmap(self, pixmap: QPixmap):
        """
        設定優化的 pixmap
        
        Args:
            pixmap: 原始 pixmap
        """
        self.original_pixmap = pixmap
        self._update_scaled_pixmap()
    
    def _update_scaled_pixmap(self):
        """更新縮放後的 pixmap"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return
            
        current_size = self.size()
        
        # 只有在大小改變時才重新縮放
        if self.cached_size != current_size:
            transformation_mode = (
                Qt.TransformationMode.FastTransformation 
                if IMAGE_SCALE_QUALITY == "fast" 
                else Qt.TransformationMode.SmoothTransformation
            )
            
            scaled_pixmap = self.original_pixmap.scaled(
                current_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                transformation_mode
            )
            
            self.setPixmap(scaled_pixmap)
            self.cached_size = current_size
            self.cached_pixmap = scaled_pixmap
    
    def resizeEvent(self, event):
        """處理大小改變事件"""
        super().resizeEvent(event)
        # 延遲更新以避免頻繁的重新縮放
        QTimer.singleShot(50, self._update_scaled_pixmap)


class ScreenDisplayWidget(QWidget):
    """螢幕顯示元件"""
    
    def __init__(self, screen_capture: MultiThreadedScreenCapture, parent=None):
        """
        初始化螢幕顯示元件
        
        Args:
            screen_capture: 多執行緒螢幕擷取管理器
            parent: 父元件
        """
        super().__init__(parent)
        self.screen_capture = screen_capture
        self.logger = get_logger("screen_display")
        self.current_pixmap = None
        
        # UI 更新節流
        self.update_throttle_timer = QTimer()
        self.update_throttle_timer.setSingleShot(True)
        self.update_throttle_timer.timeout.connect(self._perform_ui_update)
        self.pending_pixmap = None
        
        self.setup_ui()
        self.setup_screen_capture()
    
    def setup_ui(self):
        """設定 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 使用固定尺寸的螢幕顯示標籤
        self.screen_label = FixedSizeScreenLabel(640, 640)
        self.screen_label.setStyleSheet(f"""
            QLabel {{
                background-color: {SCREEN_DISPLAY["background_color"]};
                color: white;
                font-size: 14pt;
                border: 1px solid #444444;
            }}
        """)
        
        # 設定初始文字
        self.screen_label.setText("正在連接設備...")
        
        # 將標籤放置在佈局中央，但不拉伸填滿
        layout.addWidget(self.screen_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.logger.debug("螢幕顯示 UI 設定完成")
    
    def setup_screen_capture(self):
        """設定螢幕擷取"""
        # 連接多執行緒螢幕擷取信號
        self.screen_capture.image_ready.connect(self._on_image_ready_throttled)
        self.screen_capture.error_occurred.connect(self.handle_capture_error)
        
        self.logger.debug("多執行緒螢幕擷取設定完成")
    
    def _on_image_ready_throttled(self, pixmap: QPixmap):
        """
        節流的圖片更新處理
        
        Args:
            pixmap: 新的螢幕畫面
        """
        self.pending_pixmap = pixmap
        
        # 如果節流計時器沒有運行，立即更新
        if not self.update_throttle_timer.isActive():
            self._perform_ui_update()
            self.update_throttle_timer.start(UI_UPDATE_THROTTLE)
    
    def _perform_ui_update(self):
        """執行實際的 UI 更新"""
        if self.pending_pixmap:
            self.current_pixmap = self.pending_pixmap
            # 使用固定尺寸標籤，直接設定已處理好的圖片
            self.screen_label.set_fixed_pixmap(self.current_pixmap)
            self.pending_pixmap = None
    
    def start_capture(self, interval_ms: int = 1000):
        """
        開始螢幕擷取
        
        Args:
            interval_ms: 擷取間隔（毫秒）
        """
        # 將毫秒轉換為秒
        interval_seconds = interval_ms / 1000.0
        self.screen_capture.start_capture(interval_seconds)
        self.logger.info(f"開始多執行緒螢幕擷取，間隔: {interval_ms}ms ({interval_seconds}s)")
        print(f"開始多執行緒螢幕擷取，間隔: {interval_ms}ms")
    
    def stop_capture(self):
        """停止螢幕擷取"""
        self.screen_capture.stop_capture()
        self.update_throttle_timer.stop()
        self.logger.info("多執行緒螢幕擷取已停止")
        print("多執行緒螢幕擷取已停止")
    
    def handle_capture_error(self, error_message: str):
        """
        處理擷取錯誤
        
        Args:
            error_message: 錯誤訊息
        """
        self.screen_label.setText(error_message)
        self.logger.warning(f"螢幕擷取錯誤: {error_message}")
        
        # 嚴重錯誤時停止擷取
        if any(keyword in error_message for keyword in ["ADB 未安裝", "未檢測到設備"]):
            self.stop_capture()
    
    def get_current_pixmap(self) -> QPixmap:
        """
        獲取當前顯示的畫面
        
        Returns:
            QPixmap: 當前畫面，如果沒有則返回空的 QPixmap
        """
        return self.current_pixmap if self.current_pixmap else QPixmap()