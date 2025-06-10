import json
import requests


class YeelinkLamp22Cad9Light:
    def __init__(self, ha_url, token, entity_id):
        self.tools = {
        "type": "function",
        "function": {
            "name": "ScreenLightControl",
            "description": "控制显示器挂灯，支持开关、调节亮度、调节色温和状态查询功能",
            "parameters": {
            "type": "object",
            "properties": {
                "action": {
                "type": "string",
                "description": "要执行的操作类型，从以下枚举值中选其一",
                "enum": ["turn_on", "turn_off", "set_brightness", "set_color_temp", "query_status"]
                },
                "brightness": {
                "type": "number",
                "description": "亮度，范围:1~100，步长: 1，仅当action为set_brightness时使用",
                },
                "color_temp": {
                "type": "number",
                "description": "色温，范围:2700~6500，步长: 1，仅当action为set_color_temp时使用",
                },
            },
            "required": ["action"],
            }
        }
        }
        self.ha_url = ha_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.entity_id = entity_id

        # 初始化状态属性 (可读可写)
        self._status = 'off'
        self._brightness = 1
        self._color_temperature = 2700
    
    def get_property(self):
        get_property_url = f"{self.ha_url}/api/states/{self.entity_id}"
        try:
            response = requests.get(get_property_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {self.entity_id}: {e}")
        except Exception as ex:
            print(f"Error processing entity {self.entity_id}: {ex}")
        return None
    
    def update_state(self):
        """从Home Assistant获取最新状态并更新属性"""
        state_data = self.get_property()
        if not state_data:
            return False
        
        attrs = state_data.get('attributes', {})
        # 更新开关状态 (优先使用light.on，其次根据state判断)
        self._status = attrs.get('light.on', state_data['state'] != 'off')
        # 更新亮度状态
        self._brightness = attrs.get('light.brightness')
        # 更新色温状态
        self._color_temperature = attrs.get('light.color_temperature')

        return True
    
    # 灯光状态属性
    @property
    def status(self):
        self.update_state()
        return self._status
    
    @property
    def brightness(self):
        self.update_state()
        return self._brightness
    
    @property
    def color_temperature(self):
        self.update_state()
        return self._color_temperature
    
    # 灯光控制

    def set_property(self,domain,service,payload):
        set_property_url = f"{self.ha_url}/api/services/{domain}/{service}"
        
        try:
            response = requests.post(set_property_url, headers=self.headers,json=payload, timeout=5)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {self.entity_id}: {e}")
        except Exception as ex:
            print(f"Error processing entity {self.entity_id}: {ex}")
        return None

    def set_light_brightness(self, brightness):
        payload = {
            "entity_id": self.entity_id,
            "siid": 2,
            "piid": 2,
            "value": brightness
        }
        res = self.set_property("xiaomi_miot","set_miot_property",payload)
        
        return f"亮度设置为{brightness}{'成功' if res.status_code==200 else '失败'}"

    def set_light_color_temperature(self, temperature):
        payload = {
            "entity_id": self.entity_id,
            "siid": 2,
            "piid": 3,
            "value": temperature
        }
        res = self.set_property("xiaomi_miot","set_miot_property",payload)
        
        return f"色温设置为{temperature}{'成功' if res.status_code==200 else '失败'}"
    
    def turn_on(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("switch","turn_on",payload)
        
        return f"开灯{'成功' if res.status_code==200 else '失败'}"
    
    def turn_off(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("switch","turn_off",payload)
        
        return f"关灯{'成功' if res.status_code==200 else '失败'}"
    
    def toggle(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("switch","toggle",payload)
        
        return f"开关状态切换命令发送{'成功' if res.status_code==200 else '失败'}"
    

# if __name__ == "__main__":
#     HA_URL = "http://192.168.0.18:8123"
#     ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
    
#     ENTITY_ID = "light.yeelink_lamp22_cad9_light"
#     light = YeelinkLamp22Cad9Light(HA_URL,ACCESS_TOKEN,ENTITY_ID)
#     res = light.turn_off()
#     print(res)
#     res = light.turn_on()
#     print(res)




    

        