import subprocess
import platform
import time
from typing import Callable, Dict, Any

class WifiRouter:
    def __init__(self, max_retries=3, timeout=1):
        self.tools = {
            "type": "function",
            "function": {
            "name": "RouterQuery",
            "description": "查询路由器在线的设备，返回在线设备列表",
            "parameters": {
            "type": "object",
            "properties": { },
            "required": []
            }
        }}
        self.device_map = {
            "Xiaomi14": "192.168.31.27",
            "SamsungGalaxyS21ultra": "192.168.31.143",
            "iPhoneXR": "192.168.31.76", 
        }
        self.max_retries = max_retries  # 最大重试次数
        self.timeout = timeout          # 超时时间(秒)
        self.last_update = 0
        self.cache_duration = 60        # 缓存有效期(秒)
        self._online_devices = []


    # 添加事件系统
        self._event_handlers = {
            "device_online": [],
            "device_offline": []
        }
        self._last_online = set()  # 存储上一次的在线设备集合

    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """注册事件处理器"""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].append(handler)
        else:
            print(f"Warning: Unknown event type '{event_type}'")
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """触发事件并调用所有注册的处理器"""
        if event_type not in self._event_handlers:
            return
        
        # 添加设备信息
        full_data = {
            "event_type": event_type,
        }
        full_data.update(event_data)
            
        for handler in self._event_handlers[event_type]:
            try:
                handler(full_data)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def update_state(self):
        """更新在线设备状态(带缓存机制)"""
        # 检查缓存有效期
        if time.time() - self.last_update < self.cache_duration:
            return True
        
        # 获取当前在线设备集合
        new_status = {}
        for device, ip in self.device_map.items():
            new_status[device] = self.ping_device(ip)
        
        current_online = set(device for device, online in new_status.items() if online)
        
        # 检测变化并触发事件
        if hasattr(self, '_last_online'):
            # 检测新上线设备
            for device in current_online - self._last_online:
                self._trigger_event("device_online", {
                    "device": device,
                    "ip": self.device_map[device],
                    "timestamp": time.time()
                })
            
            # 检测离线设备
            for device in self._last_online - current_online:
                self._trigger_event("device_offline", {
                    "device": device,
                    "ip": self.device_map[device],
                    "timestamp": time.time()
                })
        
        # 更新状态
        self._last_online = current_online
        self._online_devices = list(current_online)
        self.last_update = time.time()
        return True


    def ping_device(self, ip):
        """带重试机制的Ping检测"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
        
        # 计算超时毫秒数(Windows需要整数毫秒)
        timeout_val = str(int(self.timeout * 1000)) if platform.system().lower() == 'windows' else str(self.timeout)
        
        command = ['ping', param, '1', timeout_param, timeout_val, ip]
        
        for _ in range(self.max_retries):
            try:
                response = subprocess.call(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=self.timeout + 1  # 额外1秒缓冲
                )
                if response == 0:
                    return True
            except subprocess.TimeoutExpired:
                continue  # 超时后重试
            except Exception as e:
                print(f"Ping error ({ip}): {str(e)}")
                break
        return False


    @property
    def online_devices(self):
        """带缓存的在线设备查询"""
        self.update_state()
        return self._online_devices








