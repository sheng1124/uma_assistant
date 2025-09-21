"""
Uma Assistant - 賽馬娘自動化助手
主程式入口點
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

# 添加專案根目錄到 Python 路徑
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from gui.main_window import MainWindow
from utils.logger import get_logger
from config.settings import APP_NAME, APP_VERSION

def main():
    """
    主程式進入點
    初始化並啟動 Uma Assistant 應用程式
    """
    # 設定應用程式基本資訊
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("Uma Assistant Team")
    
    # 獲取日誌記錄器
    logger = get_logger("main")
    logger.info(f"啟動 {APP_NAME} v{APP_VERSION}")
    
    try:
        # 創建並顯示主視窗
        main_window = MainWindow()
        main_window.show()
        
        # 執行應用程式
        exit_code = app.exec()
        logger.info(f"{APP_NAME} 正常結束")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"應用程式啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()