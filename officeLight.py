import json
import logging
import uuid
import time
from config import HOME_ASSISTANT_TOKEN

import requests


# 控制设备函数的具体实现，使用Home Assistant的Restful API
# 具体见文档https://developers.home-assistant.io/docs/api/rest/
# 小米参数 https://home.miot-spec.com/
class OfficeLight:
    def __init__(self, token):
                self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def corridor_turn_on(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_right_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_on"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def corridor_turn_off(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_right_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_off"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def main_turn_on(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_middle_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_on"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def main_turn_off(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_middle_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_off"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def side_turn_on(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_left_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_on"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def side_turn_off(self):
        payload = json.dumps({
            "entity_id": "switch.xiaomi_2wpro3_de32_left_switch_service"            
        })
        url = "http://192.168.0.35:8123/api/services/switch/turn_off"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    

