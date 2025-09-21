"""
終端介面元件
顯示應用程式輸出和日誌資訊的終端
"""

import sys
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QTextCursor, QFont

from config.ui_config import TERMINAL_STYLE
from utils.logger import get_logger


class OutputRedirector(QObject):
    """重定向 print() 輸出到 QTextEdit 的類別"""
    
    output_signal = Signal(str)
    
    def write(self, text):
        """寫入文字時觸發信號"""
        if text.strip():  # 只有非空白內容才發送信號
            self.output_signal.emit(text)
    
    def flush(self):
        """清空緩衝區（兼容性方法）"""
        pass


class TerminalWidget(QTextEdit):
    """終端介面元件"""
    
    def __init__(self, parent=None):
        """
        初始化終端元件
        
        Args:
            parent: 父元件
        """
        super().__init__(parent)
        self.logger = get_logger("terminal_widget")
        self.original_stdout = None
        self.output_redirector = None
        
        # 輸出緩衝和節流
        self.output_buffer = []
        self.flush_timer = QTimer()
        self.flush_timer.setSingleShot(True)
        self.flush_timer.timeout.connect(self._flush_buffer)
        self.max_lines = 1000  # 最大行數限制
        
        self.setup_ui()
        self.setup_output_redirection()
    
    def setup_ui(self):
        """設定 UI 樣式"""
        self.setReadOnly(True)
        self.setMaximumHeight(TERMINAL_STYLE["max_height"])
        
        # 套用樣式
        style = f"""
            QTextEdit {{
                background-color: {TERMINAL_STYLE["background_color"]};
                color: {TERMINAL_STYLE["text_color"]};
                font-family: {TERMINAL_STYLE["font_family"]};
                font-size: {TERMINAL_STYLE["font_size"]};
                border: {TERMINAL_STYLE["border"]};
            }}
        """
        self.setStyleSheet(style)
        
        # 設定字體為等寬字體
        font = QFont("Consolas")
        if not font.exactMatch():
            font = QFont("Courier New")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        self.logger.debug("終端介面 UI 設定完成")
    
    def setup_output_redirection(self):
        """設定 print() 輸出重定向到終端區域"""
        self.output_redirector = OutputRedirector()
        self.output_redirector.output_signal.connect(self.append_text)
        
        # 保存原始的 stdout 以便需要時恢復
        self.original_stdout = sys.stdout
        sys.stdout = self.output_redirector
        
        self.logger.debug("輸出重定向設定完成")
    
    def append_text(self, text: str):
        """
        添加文字到終端（使用緩衝機制）
        
        Args:
            text: 要添加的文字
        """
        # 移除末尾的換行符
        text = text.rstrip()
        if text:
            self.output_buffer.append(text)
            
            # 如果緩衝區太大或者定時器沒有運行，立即刷新
            if len(self.output_buffer) > 10 or not self.flush_timer.isActive():
                self._flush_buffer()
            else:
                # 延遲刷新以減少 UI 更新頻率
                self.flush_timer.start(100)
    
    def _flush_buffer(self):
        """刷新輸出緩衝區"""
        if not self.output_buffer:
            return
            
        # 批量添加文字
        combined_text = '\n'.join(self.output_buffer)
        self.append(combined_text)
        self.output_buffer.clear()
        
        # 限制行數以避免記憶體問題
        if self.document().lineCount() > self.max_lines:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, 
                              QTextCursor.MoveMode.KeepAnchor, 
                              self.document().lineCount() - self.max_lines)
            cursor.removeSelectedText()
        
        # 自動滾動到底部
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
    
    def clear_terminal(self):
        """清除終端內容"""
        self.clear()
        self.output_buffer.clear()
        self.flush_timer.stop()
        self.logger.debug("終端內容已清除")
        print("終端已清除")  # 這會顯示在清除後的終端中
    
    def write_line(self, text: str):
        """
        直接寫入一行文字到終端（不透過 stdout 重定向）
        
        Args:
            text: 要寫入的文字
        """
        self.append_text(text + "\n")
    
    def restore_stdout(self):
        """恢復原始的 stdout"""
        if self.original_stdout:
            sys.stdout = self.original_stdout
            self.logger.debug("stdout 已恢復")
    
    def closeEvent(self, event):
        """關閉事件處理"""
        self.restore_stdout()
        super().closeEvent(event)