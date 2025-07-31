# uma_assistant
uma derby auto script

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