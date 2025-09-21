"""
控制面板元件
包含應用程式的主要控制功能
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QGroupBox, QHBoxLayout
)
from PySide6.QtCore import Signal, Qt

from config.ui_config import BUTTON_STYLES, CONTROL_PANEL
from utils.logger import get_logger


class ControlPanelWidget(QWidget):
    """控制面板元件"""
    
    # 信號定義
    start_automation_requested = Signal(dict)  # 開始自動化，傳遞參數字典
    stop_automation_requested = Signal()  # 停止自動化
    reconnect_device_requested = Signal()  # 重新連接設備
    screenshot_requested = Signal()  # 截圖請求
    clear_terminal_requested = Signal()  # 清除終端
    
    def __init__(self, parent=None):
        """
        初始化控制面板
        
        Args:
            parent: 父元件
        """
        super().__init__(parent)
        self.logger = get_logger("control_panel")
        
        self.setup_ui()
    
    def setup_ui(self):
        """設定 UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 設定最小寬度
        self.setMinimumWidth(CONTROL_PANEL["min_width"])
        
        # 自動化參數設定區域
        self.create_automation_params_group(main_layout)
        
        # 設備控制區域
        self.create_device_control_group(main_layout)
        
        # 自動化控制區域
        self.create_automation_control_group(main_layout)
        
        # 工具區域
        self.create_tools_group(main_layout)
        
        self.logger.debug("控制面板 UI 設定完成")
    
    def create_automation_params_group(self, parent_layout):
        """創建自動化參數設定區域"""
        group = QGroupBox("自動化參數")
        layout = QFormLayout(group)
        
        # 參數一（文字輸入）
        self.param1_input = QLineEdit("預設值")
        self.param1_input.setPlaceholderText("輸入文字參數...")
        layout.addRow("參數一 (文字):", self.param1_input)
        
        # 參數二（數字輸入）
        self.param2_input = QSpinBox()
        self.param2_input.setRange(0, 100)
        self.param2_input.setValue(10)
        self.param2_input.setSuffix(" 次")
        layout.addRow("參數二 (數字):", self.param2_input)
        
        # 訓練模式選擇
        self.training_mode_input = QLineEdit("速度訓練")
        self.training_mode_input.setPlaceholderText("速度、耐力、力量、根性、智力")
        layout.addRow("訓練模式:", self.training_mode_input)
        
        parent_layout.addWidget(group)
    
    def create_device_control_group(self, parent_layout):
        """創建設備控制區域"""
        group = QGroupBox("設備連接")
        layout = QVBoxLayout(group)
        
        # 重新連接按鈕
        self.reconnect_button = QPushButton("重新連接設備")
        self.reconnect_button.setStyleSheet(BUTTON_STYLES["secondary"])
        self.reconnect_button.clicked.connect(self.reconnect_device_requested.emit)
        layout.addWidget(self.reconnect_button)
        
        # 設備狀態標籤
        self.device_status_label = QLabel("設備狀態: 未連接")
        self.device_status_label.setStyleSheet("color: #d13438; font-weight: bold;")
        layout.addWidget(self.device_status_label)
        
        parent_layout.addWidget(group)
    
    def create_automation_control_group(self, parent_layout):
        """創建自動化控制區域"""
        group = QGroupBox("自動化控制")
        layout = QVBoxLayout(group)
        
        # 開始/停止按鈕
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("開始自動化")
        self.start_button.setStyleSheet(BUTTON_STYLES["primary"])
        self.start_button.clicked.connect(self.on_start_automation)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止自動化")
        self.stop_button.setStyleSheet(BUTTON_STYLES["danger"])
        self.stop_button.clicked.connect(self.stop_automation_requested.emit)
        self.stop_button.setEnabled(False)  # 初始狀態下禁用
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        # 自動化狀態標籤
        self.automation_status_label = QLabel("自動化狀態: 已停止")
        self.automation_status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.automation_status_label)
        
        parent_layout.addWidget(group)
    
    def create_tools_group(self, parent_layout):
        """創建工具區域"""
        group = QGroupBox("工具")
        layout = QVBoxLayout(group)
        
        # 截圖按鈕
        self.screenshot_button = QPushButton("拍攝截圖")
        self.screenshot_button.setStyleSheet(BUTTON_STYLES["secondary"])
        self.screenshot_button.clicked.connect(self.screenshot_requested.emit)
        layout.addWidget(self.screenshot_button)
        
        # 清除終端按鈕
        self.clear_terminal_button = QPushButton("清除終端")
        self.clear_terminal_button.setStyleSheet(BUTTON_STYLES["secondary"])
        self.clear_terminal_button.clicked.connect(self.clear_terminal_requested.emit)
        layout.addWidget(self.clear_terminal_button)
        
        parent_layout.addWidget(group)
    
    def on_start_automation(self):
        """處理開始自動化按鈕點擊"""
        # 收集參數
        params = {
            "param1": self.param1_input.text(),
            "param2": self.param2_input.value(),
            "training_mode": self.training_mode_input.text(),
        }
        
        self.logger.info(f"請求開始自動化，參數: {params}")
        self.start_automation_requested.emit(params)
    
    def set_device_status(self, connected: bool, device_info: str = ""):
        """
        設定設備連接狀態
        
        Args:
            connected: 是否已連接
            device_info: 設備資訊
        """
        if connected:
            status_text = f"設備狀態: 已連接"
            if device_info:
                status_text += f" ({device_info})"
            self.device_status_label.setText(status_text)
            self.device_status_label.setStyleSheet("color: #107c10; font-weight: bold;")
        else:
            self.device_status_label.setText("設備狀態: 未連接")
            self.device_status_label.setStyleSheet("color: #d13438; font-weight: bold;")
    
    def set_automation_status(self, running: bool, status_text: str = ""):
        """
        設定自動化執行狀態
        
        Args:
            running: 是否正在執行
            status_text: 狀態文字
        """
        if running:
            self.automation_status_label.setText(f"自動化狀態: {status_text or '執行中'}")
            self.automation_status_label.setStyleSheet("color: #107c10; font-weight: bold;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.automation_status_label.setText(f"自動化狀態: {status_text or '已停止'}")
            self.automation_status_label.setStyleSheet("color: #666666;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
    
    def get_automation_params(self) -> dict:
        """
        獲取當前的自動化參數
        
        Returns:
            dict: 參數字典
        """
        return {
            "param1": self.param1_input.text(),
            "param2": self.param2_input.value(),
            "training_mode": self.training_mode_input.text(),
        }