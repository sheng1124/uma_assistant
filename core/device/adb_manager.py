"""
ADB 連接管理器
負責管理與 Android 設備的 ADB 連接
"""

import subprocess
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from utils.logger import get_logger
from config.settings import ADB_DEFAULT_ADDRESS, ADB_CONNECTION_TIMEOUT, ADB_RETRY_ATTEMPTS


@dataclass
class DeviceInfo:
    """設備資訊"""
    address: str
    status: str
    model: Optional[str] = None
    android_version: Optional[str] = None


class ADBManager:
    """ADB 連接管理器"""
    
    def __init__(self):
        self.logger = get_logger("adb_manager")
        self.connected_device = None
        
    def kill_server(self) -> bool:
        """
        終止 ADB 伺服器
        
        Returns:
            bool: 操作是否成功
        """
        try:
            subprocess.run(
                ['adb', 'kill-server'], 
                check=True, 
                capture_output=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            self.logger.info("ADB 伺服器已終止")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"終止 ADB 伺服器失敗: {e}")
            return False
        except FileNotFoundError:
            self.logger.error("找不到 ADB 命令，請檢查 ADB 是否已安裝並加入 PATH")
            return False
    
    def start_server(self) -> bool:
        """
        啟動 ADB 伺服器
        
        Returns:
            bool: 操作是否成功
        """
        try:
            subprocess.run(
                ['adb', 'start-server'], 
                check=True, 
                capture_output=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            self.logger.info("ADB 伺服器已啟動")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"啟動 ADB 伺服器失敗: {e}")
            return False
        except FileNotFoundError:
            self.logger.error("找不到 ADB 命令，請檢查 ADB 是否已安裝並加入 PATH")
            return False
    
    def get_devices(self) -> List[DeviceInfo]:
        """
        獲取所有連接的設備列表
        
        Returns:
            List[DeviceInfo]: 設備資訊列表
        """
        devices = []
        try:
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                check=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            lines = result.stdout.strip().split('\n')[1:]  # 跳過標題行
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) >= 2:
                    address = parts[0]
                    status = parts[1]
                    
                    # 解析額外資訊
                    model = None
                    if len(parts) > 2:
                        for part in parts[2:]:
                            if part.startswith('model:'):
                                model = part.split(':', 1)[1]
                                break
                    
                    devices.append(DeviceInfo(
                        address=address,
                        status=status,
                        model=model
                    ))
                        
        except subprocess.CalledProcessError as e:
            self.logger.error(f"獲取設備列表失敗: {e}")
        except FileNotFoundError:
            self.logger.error("找不到 ADB 命令")
            
        return devices
    
    def connect_device(self, address: Optional[str] = None) -> bool:
        """
        連接到指定設備
        
        Args:
            address: 設備地址，預設使用 ADB_DEFAULT_ADDRESS
            
        Returns:
            bool: 連接是否成功
        """
        if address is None:
            address = ADB_DEFAULT_ADDRESS
            
        for attempt in range(ADB_RETRY_ATTEMPTS):
            try:
                # 如果是網路地址，需要先連接
                if ':' in address and not address.startswith('emulator-'):
                    subprocess.run(
                        ['adb', 'connect', address],
                        check=True,
                        capture_output=True,
                        timeout=ADB_CONNECTION_TIMEOUT,
                        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
                    )
                    time.sleep(2)  # 等待連接建立
                
                # 檢查設備是否可用
                devices = self.get_devices()
                for device in devices:
                    if device.address == address and device.status == 'device':
                        self.connected_device = device
                        self.logger.info(f"成功連接到設備: {address}")
                        return True
                        
                self.logger.warning(f"連接嘗試 {attempt + 1}/{ADB_RETRY_ATTEMPTS} 失敗")
                if attempt < ADB_RETRY_ATTEMPTS - 1:
                    time.sleep(2)
                    
            except subprocess.CalledProcessError as e:
                self.logger.error(f"連接設備失敗 (嘗試 {attempt + 1}): {e}")
            except subprocess.TimeoutExpired:
                self.logger.error(f"連接超時 (嘗試 {attempt + 1})")
        
        self.logger.error(f"無法連接到設備: {address}")
        return False
    
    def disconnect_device(self, address: Optional[str] = None) -> bool:
        """
        斷開設備連接
        
        Args:
            address: 設備地址
            
        Returns:
            bool: 操作是否成功
        """
        if address is None and self.connected_device:
            address = self.connected_device.address
            
        if not address:
            self.logger.warning("沒有指定要斷開的設備")
            return False
            
        try:
            subprocess.run(
                ['adb', 'disconnect', address],
                check=True,
                capture_output=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            
            if self.connected_device and self.connected_device.address == address:
                self.connected_device = None
                
            self.logger.info(f"已斷開設備連接: {address}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"斷開設備連接失敗: {e}")
            return False
    
    def is_device_connected(self, address: Optional[str] = None) -> bool:
        """
        檢查設備是否已連接
        
        Args:
            address: 設備地址
            
        Returns:
            bool: 設備是否已連接
        """
        if address is None and self.connected_device:
            address = self.connected_device.address
            
        if not address:
            return False
            
        devices = self.get_devices()
        for device in devices:
            if device.address == address and device.status == 'device':
                return True
        return False
    
    def execute_shell_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """
        在連接的設備上執行 shell 命令
        
        Args:
            command: shell 命令
            timeout: 超時時間（秒）
            
        Returns:
            Tuple[bool, str, str]: (成功, stdout, stderr)
        """
        if not self.connected_device:
            return False, "", "沒有連接的設備"
            
        try:
            result = subprocess.run(
                ['adb', '-s', self.connected_device.address, 'shell', command],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            return True, result.stdout, result.stderr
            
        except subprocess.CalledProcessError as e:
            return False, e.stdout if e.stdout else "", e.stderr if e.stderr else str(e)
        except subprocess.TimeoutExpired:
            return False, "", "命令執行超時"
    
    def get_current_device(self) -> Optional[DeviceInfo]:
        """
        獲取當前連接的設備資訊
        
        Returns:
            Optional[DeviceInfo]: 設備資訊，如果沒有連接則為 None
        """
        return self.connected_device