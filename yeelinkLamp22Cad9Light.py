import json
import requests

HOME_ASSISTANT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzYTFkYWFhNDYyMzU0MDI4YjFlNzMyMjVkMGY4ODU0ZSIsImlhdCI6MTc0NzEzNDQzNSwiZXhwIjoyMDYyNDk0NDM1fQ.TRjIzXXVdn39LEyeGOgceL6ux7c408VJ83kKL0DXu1Q"

# 控制设备函数的具体实现，使用Home Assistant的Restful API
# 具体见文档https://developers.home-assistant.io/docs/api/rest/
# 小米参数 https://home.miot-spec.com/
class YeelinkLamp22Cad9Light:
    def __init__(self, token):
        self.set_miot_property_url = "http://192.168.0.18:8123/api/services/xiaomi_miot/set_miot_property"
        self.call_action_url = "http://192.168.0.18:8123/api/services/xiaomi_miot/call_action"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        self.entity_id = "light.yeelink_lamp22_cad9_light"

    def set_light_brightness(self, brightness, siid=2):
        payload = json.dumps({
            "entity_id": self.entity_id,
            "siid": siid,
            "piid": 2,
            "value": brightness
        })
        response = requests.request("POST", self.set_miot_property_url, headers=self.headers, data=payload)
        return "命令已发送"

    def set_light_color_temperature(self, temperature, siid=2):
        payload = json.dumps({
            "entity_id": self.entity_id,
            "siid": siid,
            "piid": 3,
            "value": temperature
        })
        response = requests.request("POST", self.set_miot_property_url, headers=self.headers, data=payload)
        return "命令已发送"
    
    def toggle(self, siid=2):
        payload = json.dumps({
            "entity_id": self.entity_id,
            "siid": siid,
            "aiid": 1,
        })
        response = requests.request("POST", self.call_action_url, headers=self.headers, data=payload)
        return response
    
    def turn_on(self):
        payload = json.dumps({
            "entity_id": self.entity_id            
        })
        url = "http://192.168.0.18:8123/api/services/light/turn_on"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
    def turn_off(self):
        payload = json.dumps({
            "entity_id": self.entity_id            
        })
        url = "http://192.168.0.18:8123/api/services/light/turn_off"
        response = requests.request("POST", url, headers=self.headers, data=payload)
        return response
    
# Successful calls will return status code 200 or 201. Other status codes that can return are:

# 400 (Bad Request)
# 401 (Unauthorized)
# 404 (Not Found)
# 405 (Method Not Allowed)







    

        