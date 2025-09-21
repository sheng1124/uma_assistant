"""
主視窗
Uma Assistant 應用程式的主視窗
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMenuBar, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QAction

from config.ui_config import MAIN_WINDOW, CONTROL_PANEL, SCREEN_DISPLAY
from config.settings import SCREENSHOT_INTERVAL
from gui.widgets.control_panel import ControlPanelWidget
from gui.widgets.screen_display import ScreenDisplayWidget
from gui.widgets.terminal_widget import TerminalWidget
from core.device.adb_manager import ADBManager
from core.device.multithreaded_screen_capture import MultiThreadedScreenCapture
from utils.logger import get_logger


class MainWindow(QMainWindow):
    """主視窗類別"""
    
    def __init__(self):
        """初始化主視窗"""
        super().__init__()
        self.logger = get_logger("main_window")
        
        # 核心管理器
        self.adb_manager = ADBManager()
        self.screen_capture = None
        
        self.setup_ui()
        self.setup_core_managers()
        self.setup_connections()
        
        # 初始連接嘗試
        QTimer.singleShot(1000, self.try_initial_connection)
        
        self.logger.info("主視窗初始化完成")
        print("Uma Assistant 已啟動")
    
    def setup_ui(self):
        """設定使用者介面"""
        # 設定視窗屬性
        self.setWindowTitle(MAIN_WINDOW["title"])
        self.setMinimumSize(MAIN_WINDOW["min_width"], MAIN_WINDOW["min_height"])
        self.resize(MAIN_WINDOW["default_width"], MAIN_WINDOW["default_height"])
        
        # 創建選單列
        self.create_menu_bar()
        
        # 創建狀態列
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備就緒")
        
        # 創建中央元件
        self.create_central_widget()
        
        self.logger.debug("主視窗 UI 設定完成")
    
    def create_menu_bar(self):
        """創建選單列"""
        menu_bar = self.menuBar()
        
        # 檔案選單
        file_menu = menu_bar.addMenu("檔案(&F)")
        
        screenshot_action = QAction("截圖(&S)", self)
        screenshot_action.setShortcut("Ctrl+S")
        screenshot_action.triggered.connect(self.take_screenshot)
        file_menu.addAction(screenshot_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("結束(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 設備選單
        device_menu = menu_bar.addMenu("設備(&D)")
        
        reconnect_action = QAction("重新連接(&R)", self)
        reconnect_action.setShortcut("Ctrl+R")
        reconnect_action.triggered.connect(self.reconnect_device)
        device_menu.addAction(reconnect_action)
        
        # 說明選單
        help_menu = menu_bar.addMenu("說明(&H)")
        
        about_action = QAction("關於(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_central_widget(self):
        """創建中央元件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主要水平分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 創建控制面板
        self.control_panel = ControlPanelWidget()
        main_splitter.addWidget(self.control_panel)
        
        # 創建右側區域（螢幕顯示 + 終端）
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 螢幕顯示區域（稍後在 setup_core_managers 中初始化）
        self.screen_display_placeholder = QWidget()
        self.screen_display_placeholder.setMinimumHeight(400)
        right_layout.addWidget(self.screen_display_placeholder, stretch=1)
        
        # 終端區域
        self.terminal_widget = TerminalWidget()
        right_layout.addWidget(self.terminal_widget)
        
        main_splitter.addWidget(right_widget)
        
        # 設定分割器比例
        control_panel_width = int(MAIN_WINDOW["default_width"] * CONTROL_PANEL["width_ratio"])
        screen_width = MAIN_WINDOW["default_width"] - control_panel_width
        main_splitter.setSizes([control_panel_width, screen_width])
        
        # 設定中央佈局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(main_splitter)
    
    def setup_core_managers(self):
        """設定核心管理器"""
        # 初始化多執行緒螢幕擷取（使用生產者-消費者模式）
        self.screen_capture = MultiThreadedScreenCapture(self.adb_manager)
        
        # 創建螢幕顯示元件並替換佔位符
        self.screen_display = ScreenDisplayWidget(self.screen_capture)
        
        # 替換佔位符
        parent_layout = self.screen_display_placeholder.parent().layout()
        parent_layout.replaceWidget(self.screen_display_placeholder, self.screen_display)
        self.screen_display_placeholder.deleteLater()
        
        self.logger.debug("核心管理器設定完成")
    
    def setup_connections(self):
        """設定信號連接"""
        # 控制面板信號連接
        self.control_panel.start_automation_requested.connect(self.start_automation)
        self.control_panel.stop_automation_requested.connect(self.stop_automation)
        self.control_panel.reconnect_device_requested.connect(self.reconnect_device)
        self.control_panel.screenshot_requested.connect(self.take_screenshot)
        self.control_panel.clear_terminal_requested.connect(self.terminal_widget.clear_terminal)
        
        # 多執行緒螢幕擷取信號連接
        self.screen_capture.screenshot_saved.connect(self.on_screenshot_saved)
        self.screen_capture.error_occurred.connect(self.on_capture_error)
        
        self.logger.debug("信號連接設定完成")
    
    def try_initial_connection(self):
        """嘗試初始連接"""
        print("嘗試連接到預設設備...")
        if self.adb_manager.connect_device():
            device = self.adb_manager.get_current_device()
            self.control_panel.set_device_status(True, device.address if device else "")
            self.screen_display.start_capture(SCREENSHOT_INTERVAL)
            self.status_bar.showMessage("設備已連接")
            print(f"成功連接到設備: {device.address if device else '未知'}")
        else:
            self.control_panel.set_device_status(False)
            self.status_bar.showMessage("設備連接失敗")
            print("無法連接到設備，請檢查 ADB 設定和模擬器狀態")
    
    def reconnect_device(self):
        """重新連接設備"""
        print("正在重新連接設備...")
        self.status_bar.showMessage("正在重新連接...")
        
        # 停止當前的螢幕擷取
        self.screen_display.stop_capture()
        
        # 重啟 ADB 服務
        self.adb_manager.kill_server()
        
        # 嘗試重新連接
        QTimer.singleShot(2000, self.try_initial_connection)  # 2秒後重試
    
    def start_automation(self, params: dict):
        """開始自動化"""
        print(f"開始自動化，參數: {params}")
        self.control_panel.set_automation_status(True, "執行中")
        self.status_bar.showMessage("自動化執行中...")
        
        # TODO: 實作自動化邏輯
        # 這裡將來要整合實際的自動化腳本
        
        self.logger.info(f"自動化已開始，參數: {params}")
    
    def stop_automation(self):
        """停止自動化"""
        print("停止自動化")
        self.control_panel.set_automation_status(False, "已停止")
        self.status_bar.showMessage("自動化已停止")
        
        # TODO: 實作停止自動化的邏輯
        
        self.logger.info("自動化已停止")
    
    def take_screenshot(self):
        """拍攝截圖"""
        print("正在拍攝截圖...")
        self.screen_capture.save_screenshot()
    
    def on_screenshot_saved(self, message: str):
        """截圖儲存成功的處理"""
        self.status_bar.showMessage(message, 3000)  # 顯示3秒
        print(message)
    
    def on_capture_error(self, error_message: str):
        """螢幕擷取錯誤處理"""
        self.status_bar.showMessage(f"螢幕擷取錯誤: {error_message}", 5000)
        
        # 如果是設備連接問題，更新設備狀態
        if "未檢測到設備" in error_message or "ADB" in error_message:
            self.control_panel.set_device_status(False)
    
    def show_about(self):
        """顯示關於對話框"""
        from config.settings import APP_NAME, APP_VERSION, APP_AUTHOR
        
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p>版本: {APP_VERSION}</p>
        <p>作者: {APP_AUTHOR}</p>
        <br>
        <p>一個用於賽馬娘遊戲的自動化助手和遊戲記錄工具。</p>
        <p>支援自動化腳本執行、影像識別、OCR 文字識別和遊戲數據記錄。</p>
        """
        
        QMessageBox.about(self, "關於 Uma Assistant", about_text)
    
    def closeEvent(self, event):
        """視窗關閉事件"""
        self.logger.info("正在關閉應用程式...")
        
        # 停止螢幕擷取
        if self.screen_display:
            self.screen_display.stop_capture()
        
        # 停止多執行緒螢幕擷取系統
        if hasattr(self, 'screen_capture') and self.screen_capture:
            self.screen_capture.cleanup()
        
        # 恢復 stdout
        if self.terminal_widget:
            self.terminal_widget.restore_stdout()
        
        # 斷開設備連接
        if self.adb_manager and self.adb_manager.get_current_device():
            self.adb_manager.disconnect_device()
        
        print("Uma Assistant 已關閉")
        event.accept()