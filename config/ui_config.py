"""
UI 相關配置
包含使用者介面的設定和樣式
"""

# 主視窗設定
MAIN_WINDOW = {
    "title": "Uma Assistant - 賽馬娘自動化助手",
    "min_width": 1000,
    "min_height": 600,
    "default_width": 1200,
    "default_height": 720,
}

# 控制面板設定
CONTROL_PANEL = {
    "width_ratio": 0.3,  # 佔主視窗寬度的比例
    "min_width": 300,
}

# 螢幕顯示區域設定
SCREEN_DISPLAY = {
    "width_ratio": 0.7,  # 佔主視窗寬度的比例
    "aspect_ratio": 9/16,  # 手機螢幕比例
    "background_color": "black",
}

# 終端機樣式
TERMINAL_STYLE = {
    "background_color": "#1e1e1e",
    "text_color": "#ffffff",
    "font_family": "Consolas, 'Courier New', monospace",
    "font_size": "10pt",
    "border": "1px solid #444444",
    "max_height": 200,
}

# 按鈕樣式
BUTTON_STYLES = {
    "primary": """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """,
    "secondary": """
        QPushButton {
            background-color: #f3f2f1;
            color: #323130;
            border: 1px solid #d2d0ce;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #edebe9;
        }
        QPushButton:pressed {
            background-color: #e1dfdd;
        }
    """,
    "danger": """
        QPushButton {
            background-color: #d13438;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #a4262c;
        }
        QPushButton:pressed {
            background-color: #8b1f23;
        }
    """
}

# 狀態列設定
STATUS_BAR = {
    "height": 30,
    "background_color": "#f8f8f8",
    "border_top": "1px solid #d4d4d4",
}

# 對話框設定
DIALOGS = {
    "settings": {
        "title": "設定",
        "width": 600,
        "height": 400,
    },
    "about": {
        "title": "關於 Uma Assistant",
        "width": 400,
        "height": 300,
    }
}

# 圖示檔案路徑
ICONS = {
    "app_icon": "icons/app.ico",
    "start": "icons/play.png",
    "stop": "icons/stop.png",
    "screenshot": "icons/camera.png",
    "settings": "icons/settings.png",
    "connect": "icons/connect.png",
    "disconnect": "icons/disconnect.png",
}