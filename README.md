# Uma Assistant - 賽馬娘自動化助手

Uma Assistant 是一個專為賽馬娘（Umamusume）遊戲設計的自動化助手和遊戲記錄工具。本軟體提供高效且流暢的自動化腳本執行功能，以及完整的遊戲數據記錄和分析功能。

## 🎯 專案目標

### 自動化功能
- **智能自動化腳本**：透過截圖和影像識別技術，自動執行遊戲中的重複性操作
- **OCR 文字識別**：支援中文 OCR 引擎，精確識別遊戲中的文字資訊
- **影像模板匹配**：使用影像識別技術，準確定位和點擊遊戲元素
- **自動化流程管理**：支援複雜的自動化流程設計和執行

### 遊戲記錄輔助
- **資料庫存儲**：完整記錄遊戲中的數據化結構和訓練記錄
- **操作日誌**：詳細記錄腳本執行的每個操作和識別到的數值
- **數據分析**：提供遊戲數據的統計和分析功能
- **歷史追蹤**：長期保存遊戲記錄，支援數據查詢和回顧

## 🏗️ 專案架構

```
uma_assistant/
├── main.py                    # 主程式入口點
├── config/                    # 配置文件
│   ├── settings.py           # 全域設定
│   ├── game_config.py        # 遊戲相關設定
│   └── ui_config.py          # UI 設定
├── core/                      # 核心模組
│   ├── automation/            # 自動化核心
│   │   ├── base_automation.py # 自動化基底類別
│   │   ├── game_automation.py # 賽馬娘遊戲自動化
│   │   └── script_manager.py  # 腳本管理器
│   ├── device/                # 設備管理
│   │   ├── adb_manager.py     # ADB 連接管理
│   │   ├── device_controller.py # 設備控制
│   │   ├── screen_capture.py  # 傳統螢幕擷取 (已棄用)
│   │   └── multithreaded_screen_capture.py # 多執行緒螢幕擷取系統
│   ├── vision/                # 影像處理與識別
│   │   ├── ocr_engine.py      # OCR 引擎
│   │   ├── image_processor.py # 影像處理
│   │   ├── template_matcher.py # 模板匹配
│   │   └── game_recognizer.py # 遊戲畫面識別
│   └── database/              # 資料庫管理
│       ├── models.py          # 資料模型
│       └── database_manager.py # 資料庫管理器
├── gui/                       # 使用者介面
│   ├── main_window.py         # 主視窗
│   └── widgets/               # UI 元件
│       ├── control_panel.py   # 控制面板
│       ├── screen_display.py  # 螢幕顯示
│       └── terminal_widget.py # 終端介面
├── utils/                     # 工具函式
│   ├── logger.py              # 日誌系統
│   ├── file_utils.py          # 檔案操作工具
│   └── image_utils.py         # 影像工具
└── data/                      # 資料目錄
    ├── database/              # 資料庫檔案
    ├── templates/             # 影像模板
    ├── logs/                  # 日誌檔案
    └── screenshots/           # 截圖檔案
```

## 🚀 快速開始

### 1. 環境需求
- Python 3.8+
- Windows 10/11 (推薦)
- Android Debug Bridge (ADB)
- MuMu Player 12 或其他 Android 模擬器

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 執行程式
```bash
python main.py
```

### 4. 性能優化特色
- **高效螢幕擷取**：多執行緒架構確保流暢的實時螢幕顯示
- **固定顯示尺寸**：640x640 固定顯示區域，避免自動縮放造成的延遲
- **即時截圖功能**：獨立的截圖系統，支援一鍵即時截圖保存

## 💡 主要功能

### 🔧 自動化控制
- **一鍵啟動**：簡單的參數設定，快速開始自動化
- **實時監控**：即時顯示設備畫面和自動化狀態
- **靈活配置**：支援多種自動化模式和參數調整

### � 高效能螢幕擷取
- **多執行緒架構**：生產者-消費者模式確保流暢運行
- **固定尺寸顯示**：640x640 固定顯示區域，保持穩定比例
- **即時截圖**：獨立截圖功能，不依賴顯示佇列，支援即時保存
- **智能節流**：UI 更新節流機制，減少不必要的重繪

### �📊 數據管理
- **完整記錄**：自動記錄訓練數據、比賽結果和重要事件
- **數據查詢**：方便的數據查詢和篩選功能
- **統計分析**：提供詳細的數據統計和趨勢分析

### 🖥️ 使用者介面
- **直觀設計**：清晰的操作界面，易於上手
- **實時反饋**：即時顯示操作狀態和執行結果
- **日誌輸出**：詳細的操作日誌，便於除錯和監控
- **響應式設計**：多執行緒確保 UI 永不凍結，操作流暢

## ⚙️ 技術特色

### 🎯 高效能多執行緒架構
- **生產者-消費者模式**：採用多執行緒生產者-消費者架構，大幅提升性能
- **專用螢幕擷取執行緒**：獨立的生產者執行緒負責定期截圖和圖片處理
- **UI 響應優化**：主執行緒專注於 UI 更新，確保界面流暢不卡頓
- **執行緒安全通信**：使用 Queue 實現執行緒間的安全資料傳遞
- **固定尺寸顯示**：螢幕顯示區域使用固定 640x640 尺寸，避免自動縮放問題

### 🖼️ 智能影像處理系統
- **預縮放技術**：生產者端預先生成多種常用尺寸，減少實時縮放開銷
- **快速圖片處理**：支援快速和高品質兩種變換模式，平衡速度與品質
- **即時截圖功能**：獨立的即時截圖系統，不依賴生產者佇列
- **錯誤恢復機制**：完善的錯誤處理和自動重試機制

### 🧠 智能自動化
- 基於狀態機的自動化流程控制
- 支援條件判斷和分支邏輯
- 錯誤自動恢復和重試機制

### 📚 擴展性設計
- 模組化架構，易於擴展新功能
- 插件系統支持，方便新增自動化腳本
- 完整的API設計，支援第三方整合

# 安裝

本腳本需要使用 Google 的 Android Debug Bridge (`adb`) 來與您的 Android 裝置或模擬器進行通訊。請依照您作業系統的指示進行安裝與設定。

## 1. 下載 Android SDK Platform-Tools

首先，請至官方網站下載對應您作業系統的 Platform-Tools：

-   [Android SDK Platform-Tools 下載頁面](https://developer.android.com/studio/releases/platform-tools)

下載完成後，將其解壓縮到一個您方便存取且不會輕易移動或刪除的位置。

**建議路徑：**
-   **Windows:** `C:\platform-tools`
-   **macOS / Linux:** `~/platform-tools` (即您的家目錄)

---

## 2. 設定環境變數

為了讓系統可以在任何路徑下都能找到 `adb` 指令，需要將其所在目錄加入到環境變數 `PATH` 中。

### Windows

1.  在開始功能表搜尋「編輯系統環境變數」並開啟它。
2.  在「系統內容」視窗中，點擊「進階」分頁，然後點擊「環境變數」。
3.  在「系統變數」區塊中，找到並選取 `Path` 變數，然後點擊「編輯」。
4.  在「編輯環境變數」視窗中，點擊「新增」，然後輸入您先前解壓縮 `platform-tools` 的完整路徑 (例如：`C:\platform-tools`)。
5.  點擊所有視窗的「確定」以儲存設定。
6.  **重新開啟**一個新的命令提示字元 (CMD) 或 PowerShell 視窗，輸入 `adb version` 並按下 Enter。如果看到版本資訊，表示設定成功。

### macOS

1.  開啟「終端機」(Terminal) 應用程式。
2.  根據您使用的 Shell，編輯對應的設定檔。預設為 Zsh (`.zshrc`)。
    ```bash
    # 如果您使用 Zsh (預設)
    nano ~/.zshrc

    # 如果您使用 Bash
    nano ~/.bash_profile
    ```
3.  在檔案的最下方加入以下這行，請將 `~/platform-tools` 替換成您實際的路徑：
    ```bash
    export PATH=$PATH:~/platform-tools
    ```
4.  按下 `Ctrl + X`，接著按 `Y` 和 `Enter` 儲存並離開。
5.  讓設定立即生效，請執行以下指令或重開終端機：
    ```bash
    # 對應您的設定檔
    source ~/.zshrc
    # 或 source ~/.bash_profile
    ```
6.  輸入 `adb version` 並按下 Enter，看到版本資訊即表示成功。

### Linux

1.  開啟您的終端機。
2.  編輯您 Shell 的設定檔，通常是 `.bashrc`。
    ```bash
    nano ~/.bashrc
    ```
3.  在檔案的最下方加入以下這行，請將 `~/platform-tools` 替換成您實際的路徑：
    ```bash
    export PATH=$PATH:~/platform-tools
    ```
4.  儲存檔案並關閉編輯器。
5.  執行 `source ~/.bashrc` 或重開終端機來套用變更。
6.  輸入 `adb version` 並按下 Enter，看到版本資訊即表示成功。

---

# 安裝與設定模擬器

本腳本建議使用 **MuMu Player 12** 作為執行遊戲的模擬器。請依照以下步驟進行安裝與設定。

## 1. 下載並安裝 MuMu Player 12

請至官方網站下載最新版本的 MuMu Player 12 並完成安裝。

-   [MuMu Player 官方網站](https://mumu.163.com/)

## 2. 設定模擬器以啟用 ADB 連線

為了讓腳本可以控制模擬器，您需要啟用「USB 偵錯」功能。詳細步驟可參考 [MuMu Player 開發者必看手冊](https://www.mumuplayer.com/tw/help/win/developers-essentials-manual.html)。

1.  開啟 MuMu Player 12。
2.  點擊模擬器視窗右上角的選單圖示 (三條線)。
3.  選擇「設定中心」。
4.  前往「開發者選項」分頁。
5.  找到並開啟「USB 偵錯」的開關。
6.  模擬器可能會提示需要重新啟動，請依照指示操作。

## 3. 驗證 ADB 連線

設定完成後，您可以透過以下指令來確認電腦是否成功連接到模擬器：

1.  開啟一個新的命令提示字元 (CMD) 或 PowerShell / 終端機。
2.  輸入以下指令：
    ```bash
    adb devices
    ```
3.  如果連線成功，您會看到類似以下的輸出，其中 `127.0.0.1:xxxxx` 代表您的模擬器裝置：
    ```
    List of devices attached
    127.0.0.1:16384	device
    ```
如果裝置列表為空，請重新檢查 MuMu Player 的「USB 偵錯」設定是否已開啟，並確認 `adb` 環境變數是否設定正確。

# 其他參考資料

- [ok-derby](https://github.com/Akegarasu/ok-derby/tree/main?tab=readme-ov-file)：另一個自動賽馬娘 Derby 腳本，提供自動化訓練功能。
- [UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer/tree/dev)：自動訓練賽馬娘的腳本，支援多種自動化操作。
- [UmaHelper](https://github.com/fedkwan/UmaHelper)：賽馬娘輔助工具，包含自動化與輔助功能。