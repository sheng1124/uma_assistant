import time
import os
import uiautomator2 as u2
from method.text_handler import *
import onnxruntime as ort
import cv2

# ort.set_default_logger_severity(3)
# # ocr = ddddocr.DdddOcr()

# d = u2.connect("127.0.0.1:16384")
# screen = d.screenshot(format="opencv")
# # screen = cv2.imread("x.png")


# print(screen.shape)
# cropped_image = screen[934:974, 636:675]
# cv2.imwrite("cut" + str(time.time()) + ".png", cropped_image)

# # text_recognizer = TextRecognizer(cropped_image, ocr)
# # x = text_recognizer.find_text_from_image()
# # print(x)



# adb kill-server
def adb_kill_server():
    """Kills the adb server."""
    cmd = 'adb kill-server'
    os.system(cmd)
    print("ADB server killed.")


# 取得所有模擬器名稱與狀態
def adb_devices():
    cmd = 'adb devices'
    process = os.popen(cmd)
    result = process.read().split('\n')
    text = []
    for line in result:
        if 'List of devices' not in line and line != '' and line != ' ':  # 去掉標題跟空白字串
            text.append(line)
    devices = {}
    for i in range(len(text)):
        words = text[i].split('\t')  # 格式: emulator-5554\tdevice
        if len(words) > 1 and 'device' in words[1]:  # 只存有啟動的模擬器
            devices[i] = words[0]  # 用模擬器index當key
    if len(devices) == 0:
        print('無啟動中的模擬器，請檢查')
        raise RuntimeError('無啟動中的模擬器，請檢查')
    return devices

# 連接單一模擬器
# emulator: 模擬器名稱
def connect_single_device(emulator: str):
    try:
        d = u2.connect(emulator)
        return d
    except:
        print('無法連接模擬器')
        raise Exception


# 連上模擬器後的操作函數

def click_on_coordinate(d, x, y):
    """
    點擊指定座標
    d: uiautomator2 device object
    x: x-coordinate
    y: y-coordinate
    """
    print(f"點擊座標: ({x}, {y})")
    d.click(x, y)
    time.sleep(1)

def click_on_text(d, text, timeout=10):
    """
    透過文字尋找並點擊UI元件
    d: uiautomator2 device object
    text: a string of text to find
    timeout: seconds to wait for the element
    """
    print(f"嘗試點擊文字: '{text}'")
    try:
        element = d(text=text)
        if element.wait(timeout=timeout):
            element.click()
            print(f"成功點擊文字: '{text}'")
        else:
            print(f"在 {timeout} 秒內找不到文字為 '{text}' 的元件")
    except u2.exceptions.UiObjectNotFoundError:
        print(f"找不到文字為 '{text}' 的元件")
    time.sleep(1)

def input_text(d, text_to_input, resource_id=None, class_name=None):
    """
    在指定的輸入框中輸入文字
    d: uiautomator2 device object
    text_to_input: the text to input
    resource_id: resource-id of the text field
    class_name: class name of the text field
    """
    print(f"輸入文字: '{text_to_input}'")
    try:
        if resource_id:
            element = d(resourceId=resource_id)
        elif class_name:
            element = d(className=class_name)
        else:
            print("請提供 resource_id 或 class_name 來定位輸入框")
            return
        
        if element.wait(timeout=10):
            element.set_text(text_to_input)
            print("文字輸入成功")
        else:
            print("在10秒內找不到輸入框")
    except u2.exceptions.UiObjectNotFoundError:
        print("找不到輸入框")

def swipe_screen(d, sx, sy, ex, ey, duration=0.5):
    """
    滑動螢幕
    d: uiautomator2 device object
    sx, sy: start coordinates
    ex, ey: end coordinates
    duration: duration of the swipe in seconds
    """
    print(f"從 ({sx}, {sy}) 滑動至 ({ex}, {ey})")
    d.swipe(sx, sy, ex, ey, duration)
    time.sleep(1)

def take_screenshot(d, save_path="screenshot.png"):
    """
    截圖並儲存
    d: uiautomator2 device object
    save_path: path to save the screenshot
    """
    print(f"截圖並儲存至 {save_path}")
    d.screenshot(save_path)

if __name__ == "__main__":
    # 重設adb server
    adb_kill_server()

    devices = adb_devices()
    for index, device in devices.items():
        print(f"Device {index}: {device}")
    # Connect to the first device (or any specific device)
    if devices:
        first_device = next(iter(devices.values()))
        d = connect_single_device(first_device)
        print(f"Connected to device: {first_device}")
        screen = d.screenshot(format="opencv")
        print(f"Screenshot taken from device: {first_device}")
        # save_path = f"cut_{first_device}_{time.time()}.png"
        save_path = f"cut_{time.time()}.png"
        cv2.imwrite(save_path, screen)
        print(f"Screenshot saved to: {save_path}")
    else:
        print("No devices found.")



    # Example usage of the adb_devices function
    # devices = adb_devices()
    # print(devices)
    
    # You can add more functionality here if needed