"""
全域設定檔案
包含應用程式的基本配置
"""

import os
from pathlib import Path

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = DATA_DIR / "logs"
DATABASE_DIR = DATA_DIR / "database"
TEMPLATES_DIR = DATA_DIR / "templates"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

# 確保資料夾存在
for dir_path in [DATA_DIR, LOG_DIR, DATABASE_DIR, TEMPLATES_DIR, SCREENSHOTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# 應用程式設定
APP_NAME = "Uma Assistant"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Uma Assistant Team"

# 日誌設定
LOG_LEVEL = "INFO"
LOG_FILE = LOG_DIR / "uma_assistant.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 資料庫設定
DATABASE_FILE = DATABASE_DIR / "uma_assistant.db"

# 螢幕截圖設定
SCREENSHOT_INTERVAL = 1000  # 毫秒，提高間隔減少負載
SCREENSHOT_QUALITY = 85  # 降低品質提高性能
SCREENSHOT_FORMAT = "PNG"
SCREENSHOT_BUFFER_SIZE = 5  # 保留最近 5 張截圖的緩存

# 性能優化設定
UI_UPDATE_THROTTLE = 100  # UI 更新節流，毫秒
MAX_CONCURRENT_SCREENSHOTS = 1  # 最大併發截圖數量
ERROR_REPORT_COOLDOWN = 5  # 錯誤報告冷卻時間，秒

# 影像處理設定
IMAGE_SCALE_QUALITY = "fast"  # fast, smooth
MAX_IMAGE_CACHE_SIZE = 50  # MB

# ADB 設定
ADB_DEFAULT_ADDRESS = "127.0.0.1:16384"
ADB_CONNECTION_TIMEOUT = 30  # 秒
ADB_RETRY_ATTEMPTS = 3

# OCR 設定
OCR_LANGUAGE = "chi_tra"  # 繁體中文
OCR_CONFIDENCE_THRESHOLD = 0.7

# UI 設定
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 720
TERMINAL_MAX_LINES = 1000