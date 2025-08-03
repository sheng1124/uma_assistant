import sys
from PySide6.QtWidgets import QApplication
from utils.ui import AndroidScriptTester

def main():
    """
    主程式進入點。
    初始化並啟動UI介面。
    """
    app = QApplication(sys.argv)
    window = AndroidScriptTester()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()