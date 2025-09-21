"""
遊戲相關配置
包含賽馬娘遊戲的特定設定和參數
"""

# 遊戲畫面解析度（預設為 MuMu Player 12）
GAME_RESOLUTION = {
    "width": 900,
    "height": 1600
}

# 遊戲畫面關鍵區域座標
GAME_REGIONS = {
    "menu_button": (50, 50, 100, 100),
    "start_button": (400, 1400, 500, 1500),
    "back_button": (50, 100, 150, 150),
    "confirm_button": (350, 1300, 550, 1400),
    "cancel_button": (150, 1300, 350, 1400),
}

# 賽馬娘訓練相關設定
TRAINING_CONFIG = {
    "auto_training": {
        "enabled": False,
        "training_type": "speed",  # speed, stamina, power, guts, wisdom
        "rest_threshold": 30,  # 體力低於此值時休息
        "skill_point_threshold": 100,  # 技能點數達到此值時學習技能
    },
    "derby_auto": {
        "enabled": False,
        "race_selection": "auto",  # auto, manual
        "equipment_selection": "best",  # best, manual
    }
}

# 影像識別模板檔案名稱
IMAGE_TEMPLATES = {
    "menu_icons": {
        "training": "training_icon.png",
        "derby": "derby_icon.png",
        "story": "story_icon.png",
        "gacha": "gacha_icon.png",
    },
    "buttons": {
        "start": "start_button.png",
        "confirm": "confirm_button.png",
        "cancel": "cancel_button.png",
        "back": "back_button.png",
    },
    "status_indicators": {
        "energy_full": "energy_full.png",
        "energy_low": "energy_low.png",
        "skill_available": "skill_available.png",
    }
}

# 文字識別關鍵詞
TEXT_PATTERNS = {
    "training_complete": ["訓練完成", "Training Complete"],
    "race_result": ["勝利", "敗北", "Victory", "Defeat"],
    "skill_learned": ["習得", "Learned"],
    "energy_recovered": ["體力回復", "Energy Recovered"],
}

# 自動化腳本間隔時間（秒）
AUTOMATION_INTERVALS = {
    "click_interval": 1.0,
    "wait_for_load": 3.0,
    "screenshot_analysis": 0.5,
    "text_recognition": 2.0,
}

# 資料收集設定
DATA_COLLECTION = {
    "save_screenshots": True,
    "save_training_logs": True,
    "save_race_results": True,
    "data_retention_days": 30,
}