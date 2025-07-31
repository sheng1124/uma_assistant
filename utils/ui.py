import sys
import subprocess
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QTimer, Qt
import uiautomator2 as u2
import warnings

from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QFormLayout, QSpinBox
)

class AndroidScriptTester(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle('Android 腳本測試工具')
        self.setGeometry(100, 100, 1200, 720)

        # 主佈局
        main_layout = QHBoxLayout(self)

        # 左側控制面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2) # 調整佔用比例

        # 右側螢幕顯示
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1) # 調整佔用比例以接近手機螢幕

    def create_left_panel(self):
        """創建左側的參數控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 參數表單
        form_layout = QFormLayout()
        self.param1_input = QLineEdit("value1")
        self.param2_input = QSpinBox()
        self.param2_input.setRange(0, 100)
        self.param2_input.setValue(10)
        
        form_layout.addRow("參數一 (文字):", self.param1_input)
        form_layout.addRow("參數二 (數字):", self.param2_input)

        # 按鈕
        self.start_button = QPushButton("開始腳本")
        self.stop_button = QPushButton("停止腳本")

        layout.addLayout(form_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        
        # 連接信號
        self.start_button.clicked.connect(self.start_script)
        self.stop_button.clicked.connect(self.stop_script)

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

    def setup_timer(self):
        """設定計時器以定期更新螢幕畫面"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_screen_adb)
        self.timer.start(500)  # 每 500 毫秒更新一次

    def update_screen_adb(self):
        """使用 ADB 截取模擬器畫面並更新"""
        try:
            # 使用 adb exec-out screencap -p 可以直接獲取 png 格式的螢幕截圖
            command = ["adb", "exec-out", "screencap", "-p"]
            process = subprocess.run(
                command,
                capture_output=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW # Windows下防止彈出命令視窗
            )
            
            image_data = process.stdout
            if not image_data:
                self.screen_label.setText("無法獲取畫面 (空數據)")
                return

            image = QImage.fromData(image_data)
            if image.isNull():
                self.screen_label.setText("無法解析圖片")
                return

            pixmap = QPixmap.fromImage(image)
            # 保持寬高比縮放
            scaled_pixmap = pixmap.scaled(
                self.screen_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.screen_label.setPixmap(scaled_pixmap)

        except FileNotFoundError:
            self.screen_label.setText("錯誤: adb 未安裝或未在 PATH 中")
            self.timer.stop()
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8', errors='ignore').strip()
            if "no devices/emulators found" in error_message:
                self.screen_label.setText("錯誤: 未檢測到設備/模擬器")
            else:
                self.screen_label.setText(f"ADB 命令錯誤:\n{error_message}")
        except Exception as e:
            self.screen_label.setText(f"發生未知錯誤: {e}")


    def update_screen(self):
        """使用 uiautomator2 截取模擬器畫面並更新"""
        try:
            # 延遲導入並在首次使用時初始化
            if not hasattr(self, 'u2'):
                # uiautomator2 可能會產生 UserWarning，在此處忽略
                warnings.simplefilter("ignore", UserWarning)
                self.u2 = u2
                self.d = self.u2.connect() # 連接到第一個可用的設備

            # 獲取螢幕截圖，返回 PIL.Image 物件
            pil_image = self.d.screenshot()
            if pil_image is None:
                self.screen_label.setText("無法獲取畫面 (空數據)")
                return

            # 將 PIL.Image 轉換為 QImage
            # 確保影像是 RGBA 格式以進行正確轉換
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
            
            image_data = pil_image.tobytes("raw", "RGBA")
            q_image = QImage(image_data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)

            if q_image.isNull():
                self.screen_label.setText("無法解析圖片")
                return

            pixmap = QPixmap.fromImage(q_image)
            
            # 保持寬高比縮放
            scaled_pixmap = pixmap.scaled(
                self.screen_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.screen_label.setPixmap(scaled_pixmap)

        except ImportError:
            self.screen_label.setText("錯誤: uiautomator2 套件未安裝\n請執行: pip install uiautomator2")
            self.timer.stop()
        except RuntimeError as e:
            # uiautomator2 在找不到設備時會拋出 RuntimeError
            self.screen_label.setText(f"錯誤: 未檢測到設備/模擬器\n{e}")
        except Exception as e:
            self.screen_label.setText(f"發生未知錯誤: {e}")
            # 考慮在發生嚴重錯誤時停止計時器
            # self.timer.stop()

    def start_script(self):
        """開始執行腳本的邏輯 (此處為示例)"""
        param1 = self.param1_input.text()
        param2 = self.param2_input.value()
        print(f"腳本開始，參數一: {param1}, 參數二: {param2}")
        # 在此處添加您的腳本執行代碼

    def stop_script(self):
        """停止執行腳本的邏輯 (此處為示例)"""
        print("腳本已停止")
        # 在此處添加您的腳本停止代碼

    def closeEvent(self, event):
        """關閉視窗時停止計時器"""
        self.timer.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidScriptTester()
    window.show()
    sys.exit(app.exec())