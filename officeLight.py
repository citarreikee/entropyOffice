import json
import requests

class OfficeLight:
    def __init__(self, ha_url, token, entity_id):
        self.ha_url = ha_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.entity_id = entity_id
        

        # 初始化状态属性 (可读可写)
        self._status = 'off'
        
        # 首次状态同步
        self.update_state()

    def update_state(self):
        """从Home Assistant获取最新状态并更新属性"""
        state_data = self.get_property()
        if not state_data:
            return False
        # 更新开关状态 
        self._status = state_data.get('state', False)
        
        return True 

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
    
    # 灯光状态属性
    @property
    def status(self):
        return self._status
    
   
    
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
    
    def turn_on(self):
        payload = {"entity_id": self.entity_id}
        self.set_property("switch","turn_on",payload)
        self.update_state()
        return f"开灯{'成功' if self.status=='on' else '失败'}"
    
    def turn_off(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("switch","turn_off",payload)
        self.update_state()
        return f"关灯{'成功' if self.status=='off' else '失败'}"
    
    def toggle(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("switch","toggle",payload)
        self.update_state()
        return f"开关状态切换命令发送{'成功' if res.status_code==200 else '失败'}"
    




    
# if __name__ == "__main__":
#     HA_URL = "http://192.168.0.18:8123"
#     ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
    
#     ENTITY_ID = "switch.xiaomi_2wpro3_de32_middle_switch_service"
#     light = Light(HA_URL, ACCESS_TOKEN, ENTITY_ID)
#     res = light.get_property()
#     print(res)
#     res = light.toggle()
#     print(res)
#     time.sleep(2)
#     res = light.turn_on()
#     print(res)
#     time.sleep(2)
#     res = light.status
#     print(res)