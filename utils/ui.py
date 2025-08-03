import sys
import os
import time
import subprocess
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QObject
import uiautomator2 as u2
import warnings

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QFormLayout, QSpinBox
)

class ScreenCaptureWorker(QObject):
    """
    在背景執行緒中執行螢幕擷取的 Worker。
    """
    image_ready = Signal(QPixmap)
    capture_error = Signal(str)
    screenshot_saved = Signal(str)

    def capture_screen_adb(self):
        """使用 ADB 截取模擬器畫面並透過信號發送"""
        try:
            command = ["adb", "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0) # 兼容非 Windows 系統
            )
            
            image_data = process.stdout
            if not image_data:
                self.capture_error.emit("無法獲取畫面 (空數據)")
                return

            image = QImage.fromData(image_data)
            if image.isNull():
                self.capture_error.emit("無法解析圖片")
                return
            
            # 顯示圖片的寬度和高度和解析度
            #print(f"截圖成功，解析度: {image.width()}x{image.height()}") #截圖成功，解析度: 900x1600

            pixmap = QPixmap.fromImage(image)
            self.image_ready.emit(pixmap)

        except FileNotFoundError:
            self.capture_error.emit("錯誤: adb 未安裝或未在 PATH 中")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8', errors='ignore').strip()
            if "no devices/emulators found" in error_message:
                self.capture_error.emit("錯誤: 未檢測到設備/模擬器")
            else:
                self.capture_error.emit(f"ADB 命令錯誤:\n{error_message}")
        except Exception as e:
            self.capture_error.emit(f"發生未知錯誤: {e}")

    def save_screenshot_to_file(self):
        """使用 ADB 截取模擬器畫面並直接儲存成檔案"""
        try:
            command = ["adb", "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            image_data = process.stdout
            if not image_data:
                self.capture_error.emit("截圖失敗 (空數據)")
                return

            image = QImage.fromData(image_data)
            if image.isNull():
                self.capture_error.emit("截圖失敗 (無法解析圖片)")
                return
            
            filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
            if image.save(filename):
                self.screenshot_saved.emit(f"螢幕截圖已儲存至 {filename}")
            else:
                self.capture_error.emit("截圖失敗 (儲存檔案時發生錯誤)")

        except Exception as e:
            self.capture_error.emit(f"截圖時發生錯誤: {e}")


class AndroidScriptTester(QWidget):
    def __init__(self):
        super().__init__()
        self.d = None # uiautomator2 device instance
        self.current_pixmap = None
        self.init_ui()
        self.setup_screen_capture_thread()

    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle('Android 腳本測試工具')
        self.setGeometry(100, 100, 1200, 720)

        main_layout = QHBoxLayout(self)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

    def create_left_panel(self):
        """創建左側的參數控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        form_layout = QFormLayout()
        self.param1_input = QLineEdit("value1")
        self.param2_input = QSpinBox()
        self.param2_input.setRange(0, 100)
        self.param2_input.setValue(10)
        
        form_layout.addRow("參數一 (文字):", self.param1_input)
        form_layout.addRow("參數二 (數字):", self.param2_input)

        self.start_button = QPushButton("開始腳本")
        self.stop_button = QPushButton("停止腳本")
        self.reconnect_button = QPushButton("重新連結模擬器")
        self.screenshot_button = QPushButton("截圖")

        layout.addLayout(form_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reconnect_button)
        layout.addWidget(self.screenshot_button)
        
        self.start_button.clicked.connect(self.start_script)
        self.stop_button.clicked.connect(self.stop_script)
        self.reconnect_button.clicked.connect(self.reconnect_device)
        self.screenshot_button.clicked.connect(self.take_screenshot)

        return panel

    def create_right_panel(self):
        """創建右側的模擬器螢幕顯示區域"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.screen_label = QLabel("正在連接模擬器...")
        self.screen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.screen_label)

        return panel

    def setup_screen_capture_thread(self):
        """設定螢幕擷取執行緒和計時器"""
        self.capture_thread = QThread()
        self.capture_worker = ScreenCaptureWorker()
        self.capture_worker.moveToThread(self.capture_thread)

        # 連接信號與槽
        self.capture_worker.image_ready.connect(self.update_screen_pixmap)
        self.capture_worker.capture_error.connect(self.handle_capture_error)
        self.capture_worker.screenshot_saved.connect(self.on_screenshot_saved)

        # 設定計時器來觸發擷取
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_worker.capture_screen_adb)
        
        # 啟動執行緒
        self.capture_thread.start()
        self.timer.start(500) # 每 500 毫秒觸發一次擷取

    def update_screen_pixmap(self, pixmap):
        """更新螢幕畫面的槽函數"""
        self.current_pixmap = pixmap
        scaled_pixmap = pixmap.scaled(
            self.screen_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.screen_label.setPixmap(scaled_pixmap)

    def handle_capture_error(self, error_message):
        """處理擷取錯誤的槽函數"""
        self.screen_label.setText(error_message)
        # 發生錯誤時可以考慮停止計時器，避免不斷顯示錯誤訊息
        if "adb 未安裝" in error_message or "未檢測到設備" in error_message:
            self.timer.stop()
            print("計時器已停止，因為檢測到嚴重錯誤。")

    def start_script(self):
        """開始執行腳本的邏輯"""
        param1 = self.param1_input.text()
        param2 = self.param2_input.value()
        print(f"腳本開始，參數一: {param1}, 參數二: {param2}")
        # 在此處添加您的腳本執行代碼

    def stop_script(self):
        """停止執行腳本的邏輯"""
        print("腳本已停止")
        # 在此處添加您的腳本停止代碼

    def reconnect_device(self):
        """重新連結模擬器/設備"""
        print("嘗試重新連接...")
        self.adb_kill_server()
        time.sleep(1) # 給予 ADB 服務重啟時間
        
        # 重新啟動計時器和執行緒（如果已停止）
        if not self.capture_thread.isRunning():
            self.capture_thread.start()
        if not self.timer.isActive():
            self.timer.start(500)
        
        # 立即觸發一次畫面更新
        self.capture_worker.capture_screen_adb()
        print("已發送重新連接與畫面更新請求。")

    def take_screenshot(self):
        """發送指令以儲存當前螢幕畫面"""
        print("正在截圖並儲存...")
        # 在工作執行緒中觸發截圖儲存，避免阻塞 UI
        QTimer.singleShot(0, self.capture_worker.save_screenshot_to_file)

    def on_screenshot_saved(self, message):
        """處理截圖儲存成功的訊息"""
        print(message)

    def adb_kill_server(self):
        """Kills the adb server."""
        try:
            subprocess.run(['adb', 'kill-server'], check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            print("ADB server killed.")
        except Exception as e:
            print(f"無法終止 ADB 服務: {e}")

    def closeEvent(self, event):
        """關閉視窗時停止計時器和執行緒"""
        self.timer.stop()
        self.capture_thread.quit()
        self.capture_thread.wait() # 等待執行緒完全結束
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidScriptTester()
    window.show()
    sys.exit(app.exec())
