import json
import logging
import uuid

from config import HOME_ASSISTANT_TOKEN

import requests


# 控制设备函数的具体实现，使用Home Assistant的Restful API
# 具体见文档https://developers.home-assistant.io/docs/api/rest/
# 小米参数 https://home.miot-spec.com/
class WifiSpaekerlx06:
    def __init__(self, token):
        self.set_miot_property_url = "http://192.168.0.35:8123/api/services/xiaomi_miot/set_miot_property"
        self.call_action_url = "http://192.168.0.35:8123/api/services/xiaomi_miot/call_action"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        self.entity_id = "remote.xiaomi_lx06_c3ba_wifispeaker"

    def play_text(self, text_to_speak):
        payload = json.dumps({
            "entity_id": self.entity_id,
            "siid": 5,
            "aiid": 1,
            "params": text_to_speak
        })
        response = requests.request("POST", self.call_action_url, headers=self.headers, data=payload)
        return response
    

    
