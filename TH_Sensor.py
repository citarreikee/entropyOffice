import json
import requests
import time
from typing import Callable, Dict, Any

class TH_Sensor:
    def __init__(self, ha_url: str, token: str, entity_id: str):
        self.tools = {
        "type": "function",
        "function": {
            "name": "TH_SensorQuery",
            "description": "查询温湿度计的读数",
            "parameters": {
            "type": "object",
            "properties": {
                "thID": {
                "type": "integer",
                "description": "要查询的温湿度计编号",
                },                
            },  
            "required": ["thID"]
            }
        }
        }
        self.ha_url = ha_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.entity_id = entity_id
        
        # 初始化状态值
        self.current_temp = 25.0
        self.humidity = 45.0
        self._last_temp = None
        self._last_humidity = None
        
        # 事件回调字典
        self._event_handlers = {
            "temp_change": [],
            "humidity_change": []
        }
        
        # 首次同步状态
        self.update_state()

    def update_state(self) -> bool:
        """从Home Assistant获取最新状态并更新属性"""
        data = self.get_property()
        if data:
            try:
                attrs = data.get('attributes', {})
                new_temp = attrs.get('temperature-2-1', self.current_temp)
                new_humidity = attrs.get('relative_humidity-2-2', self.humidity)
                
                # 检查温度变化
                if self._last_temp is not None and abs(new_temp - self._last_temp) >= 0.5:
                    self._trigger_event("temp_change", {
                        "old_temp": self._last_temp,
                        "new_temp": new_temp,
                        "delta": round(new_temp - self._last_temp, 1),
                        "timestamp": time.time()
                    })
                
                # 检查湿度变化
                if self._last_humidity is not None and abs(new_humidity - self._last_humidity) >= 0.5:
                    self._trigger_event("humidity_change", {
                        "old_humidity": self._last_humidity,
                        "new_humidity": new_humidity,
                        "delta": round(new_humidity - self._last_humidity, 1),
                        "timestamp": time.time()
                    })
                
                # 更新状态
                self.current_temp = new_temp
                self.humidity = new_humidity
                self._last_temp = new_temp
                self._last_humidity = new_humidity
                
                return True
            except Exception as e:
                print(f"Error updating state: {e}")
        return False
    
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
            "entity_id": self.entity_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event_data["timestamp"]))
        }
        full_data.update(event_data)
        
        # 调用所有处理器
        for handler in self._event_handlers[event_type]:
            try:
                handler(full_data)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def get_property(self) -> Dict:
        """从Home Assistant获取实体属性"""
        url = f"{self.ha_url}/api/states/{self.entity_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        return None
    
    @property
    def _current_temp(self) -> float:
        """获取当前温度（带自动更新）"""
        self.update_state()
        return self.current_temp
    
    @property
    def _humidity(self) -> float:
        """获取当前湿度（带自动更新）"""
        self.update_state()
        return self.humidity
    
