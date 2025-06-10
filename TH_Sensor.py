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
    
# def temp_change_handler(event_data: dict) -> None:
#     """温度变化事件处理器"""
#     print(f"🌡️ 温度变化事件 | 设备: {event_data['entity_id']}")
#     print(f"  时间: {event_data['timestamp']}")
#     print(f"  变化: {event_data['old_temp']}℃ → {event_data['new_temp']}℃")
#     print(f"  差值: {'+' if event_data['delta'] > 0 else ''}{event_data['delta']}℃")
#     print("-" * 40)

# def humidity_change_handler(event_data: dict) -> None:
#     """湿度变化事件处理器"""
#     print(f"💧 湿度变化事件 | 设备: {event_data['entity_id']}")
#     print(f"  时间: {event_data['timestamp']}")
#     print(f"  变化: {event_data['old_humidity']}% → {event_data['new_humidity']}%")
#     print(f"  差值: {'+' if event_data['delta'] > 0 else ''}{event_data['delta']}%")
#     print("-" * 40)
    
# if __name__ == "__main__":
#     HA_URL = "http://192.168.0.18:8123"
#     ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
#     ENTITY_ID = "button.miaomiaoce_t2_ceca_info"

#     sensor = TH_Sensor(HA_URL, ACCESS_TOKEN, ENTITY_ID)
#     print(sensor.current_temp)
#     print(sensor.humidity)
#     # 注册事件处理器
#     sensor.register_event_handler("temp_change", temp_change_handler)
#     sensor.register_event_handler("humidity_change", humidity_change_handler)
    
#     # 模拟持续监控
#     print("开始监控温湿度变化...")
#     while True:
#         # 更新状态（会触发事件检查）
#         sensor.update_state()
        
#         # 打印当前状态
#         print(f"\r当前温度: {sensor._current_temp:.1f}℃ | 湿度: {sensor._humidity:.1f}%", end="")
        
#         # 每10秒更新一次
#         time.sleep(10)