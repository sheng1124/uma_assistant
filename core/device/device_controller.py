"""
設備控制器
負責統一管理設備操作，如點擊、滑動、輸入等
"""

import time
import uiautomator2 as u2
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from utils.logger import get_logger
from config.game_config import AUTOMATION_INTERVALS
from core.device.adb_manager import ADBManager


@dataclass
class Point:
    """座標點"""
    x: int
    y: int


@dataclass
class Rect:
    """矩形區域"""
    left: int
    top: int
    right: int
    bottom: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    @property
    def center(self) -> Point:
        return Point(
            x=self.left + self.width // 2,
            y=self.top + self.height // 2
        )


class DeviceController:
    """設備控制器"""
    
    def __init__(self, adb_manager: ADBManager):
        """
        初始化設備控制器
        
        Args:
            adb_manager: ADB 管理器實例
        """
        self.adb_manager = adb_manager
        self.logger = get_logger("device_controller")
        self.u2_device: Optional[u2.Device] = None
        
    def connect_u2_device(self) -> bool:
        """
        連接 uiautomator2 設備
        
        Returns:
            bool: 連接是否成功
        """
        device_info = self.adb_manager.get_current_device()
        if not device_info:
            self.logger.error("沒有已連接的 ADB 設備")
            return False
            
        try:
            self.u2_device = u2.connect(device_info.address)
            self.logger.info(f"成功連接 uiautomator2 設備: {device_info.address}")
            return True
        except Exception as e:
            self.logger.error(f"連接 uiautomator2 設備失敗: {e}")
            self.u2_device = None
            return False
    
    def is_connected(self) -> bool:
        """
        檢查設備是否已連接
        
        Returns:
            bool: 設備是否已連接
        """
        if not self.u2_device:
            return False
            
        try:
            # 嘗試獲取設備資訊來檢查連接狀態
            _ = self.u2_device.info
            return True
        except Exception:
            return False
    
    def click_coordinate(self, x: int, y: int, duration: float = 0.1) -> bool:
        """
        點擊指定座標
        
        Args:
            x: x 座標
            y: y 座標
            duration: 點擊持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self.logger.error("設備未連接，無法執行點擊操作")
            return False
            
        try:
            self.logger.debug(f"點擊座標: ({x}, {y})")
            self.u2_device.click(x, y, duration)
            time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
            return True
        except Exception as e:
            self.logger.error(f"點擊座標 ({x}, {y}) 失敗: {e}")
            return False
    
    def click_point(self, point: Point, duration: float = 0.1) -> bool:
        """
        點擊指定點
        
        Args:
            point: 座標點
            duration: 點擊持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        return self.click_coordinate(point.x, point.y, duration)
    
    def click_rect_center(self, rect: Rect, duration: float = 0.1) -> bool:
        """
        點擊矩形區域的中心
        
        Args:
            rect: 矩形區域
            duration: 點擊持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        return self.click_point(rect.center, duration)
    
    def click_by_text(self, text: str, timeout: int = 10) -> bool:
        """
        透過文字尋找並點擊 UI 元件
        
        Args:
            text: 要尋找的文字
            timeout: 等待超時時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self.logger.error("設備未連接，無法執行文字點擊操作")
            return False
            
        try:
            self.logger.debug(f"嘗試點擊文字: '{text}'")
            element = self.u2_device(text=text)
            
            if element.wait(timeout=timeout):
                element.click()
                self.logger.info(f"成功點擊文字: '{text}'")
                time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
                return True
            else:
                self.logger.warning(f"在 {timeout} 秒內找不到文字為 '{text}' 的元件")
                return False
                
        except Exception as e:
            self.logger.error(f"點擊文字 '{text}' 失敗: {e}")
            return False
    
    def input_text(self, text: str, resource_id: Optional[str] = None, 
                   class_name: Optional[str] = None, clear_first: bool = True) -> bool:
        """
        在指定的輸入框中輸入文字
        
        Args:
            text: 要輸入的文字
            resource_id: 輸入框的 resource-id
            class_name: 輸入框的 class name
            clear_first: 是否先清除現有文字
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self.logger.error("設備未連接，無法執行文字輸入操作")
            return False
            
        try:
            self.logger.debug(f"輸入文字: '{text}'")
            
            if resource_id:
                element = self.u2_device(resourceId=resource_id)
            elif class_name:
                element = self.u2_device(className=class_name)
            else:
                self.logger.error("請提供 resource_id 或 class_name 來定位輸入框")
                return False
            
            if element.wait(timeout=10):
                if clear_first:
                    element.clear_text()
                element.set_text(text)
                self.logger.info("文字輸入成功")
                time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
                return True
            else:
                self.logger.error("找不到輸入框")
                return False
                
        except Exception as e:
            self.logger.error(f"輸入文字失敗: {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, 
              duration: float = 0.5) -> bool:
        """
        滑動螢幕
        
        Args:
            start_x: 起始 x 座標
            start_y: 起始 y 座標
            end_x: 結束 x 座標
            end_y: 結束 y 座標
            duration: 滑動持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self.logger.error("設備未連接，無法執行滑動操作")
            return False
            
        try:
            self.logger.debug(f"從 ({start_x}, {start_y}) 滑動至 ({end_x}, {end_y})")
            self.u2_device.swipe(start_x, start_y, end_x, end_y, duration)
            time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
            return True
        except Exception as e:
            self.logger.error(f"滑動操作失敗: {e}")
            return False
    
    def swipe_points(self, start: Point, end: Point, duration: float = 0.5) -> bool:
        """
        在兩個點之間滑動
        
        Args:
            start: 起始點
            end: 結束點
            duration: 滑動持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        return self.swipe(start.x, start.y, end.x, end.y, duration)
    
    def long_click(self, x: int, y: int, duration: float = 1.0) -> bool:
        """
        長按指定座標
        
        Args:
            x: x 座標
            y: y 座標
            duration: 長按持續時間（秒）
            
        Returns:
            bool: 操作是否成功
        """
        if not self.is_connected():
            self.logger.error("設備未連接，無法執行長按操作")
            return False
            
        try:
            self.logger.debug(f"長按座標: ({x}, {y})")
            self.u2_device.long_click(x, y, duration)
            time.sleep(AUTOMATION_INTERVALS.get('click_interval', 1.0))
            return True
        except Exception as e:
            self.logger.error(f"長按座標 ({x}, {y}) 失敗: {e}")
            return False
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """
        獲取設備資訊
        
        Returns:
            Optional[Dict[str, Any]]: 設備資訊字典
        """
        if not self.is_connected():
            return None
            
        try:
            return self.u2_device.info
        except Exception as e:
            self.logger.error(f"獲取設備資訊失敗: {e}")
            return None
    
    def wait_for_element(self, timeout: int = 10, **kwargs) -> bool:
        """
        等待元件出現
        
        Args:
            timeout: 等待超時時間（秒）
            **kwargs: 元件選擇器參數
            
        Returns:
            bool: 元件是否出現
        """
        if not self.is_connected():
            return False
            
        try:
            element = self.u2_device(**kwargs)
            return element.wait(timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待元件出現失敗: {e}")
            return False