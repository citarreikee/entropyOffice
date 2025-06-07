import json
import requests

class WifiSpaekerlx06:
    def __init__(self, ha_url, token, entity_id):
        self.ha_url = ha_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.entity_id = entity_id
        
    # 控制功能
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

    def play_text(self, text_to_speak):
        payload = {"entity_id": self.entity_id,"value":text_to_speak}
        res = self.set_property("text","set_value",payload)
        return f"播放内容{'成功' if res.status_code==200 else '失败'}"
    
if __name__ == "__main__":
    HA_URL = "http://192.168.0.18:8123"
    ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
    
    ENTITY_ID = "text.xiaomi_lx06_c3ba_play_text"
    speaker = WifiSpaekerlx06(HA_URL, ACCESS_TOKEN, ENTITY_ID)
    res = speaker.play_text("hello,瓦达西瓦孙笑川")
    print(res)
    
    

    
