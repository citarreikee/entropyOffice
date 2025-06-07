import json
import requests

class AirConditioner:
    def __init__(self, ha_url, token, entity_id):
        self.ha_url = ha_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.entity_id = entity_id
        # 属性定义 (可读可写)
        self._power_status = False  # 开关状态
        self._target_temp = 26.0    # 目标温度
        self._mode = "cool"         # 工作模式
        self._fan_speed = 2         # 风速等级
        # 只读属性
        self.current_temp = 25.0     # 当前温度
        self.humidity = 45.0         # 当前湿度
        # 首次初始化时同步状态
        self.update_state()

    def update_state(self):
        """从Home Assistant获取最新状态并更新属性"""
        state_data = self.get_property()
        if not state_data:
            return False
        
        attrs = state_data.get('attributes', {})
        # 更新开关状态 (优先使用thermostat.on，其次根据state判断)
        self._power_status = attrs.get('thermostat.on', state_data['state'] != 'off')
        # 更新目标温度
        self._target_temp = attrs.get('thermostat.target_temperature', attrs.get('temperature', 26.0))
        # 更新模式 (关闭时保留上次模式)
        if self._power_status:
            self._mode = state_data['state']
        # 更新风速 (数字等级)
        self._fan_speed = attrs.get('thermostat.fan_level', 2)
        # 更新只读属性
        self.current_temp = attrs.get('current_temperature', attrs.get('environment.temperature', 25.0))
        self.humidity = attrs.get('current_humidity', attrs.get('environment.relative_humidity', 45.0))
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

    # 属性访问器
    @property
    def power_status(self):
        
        return self._power_status
    
    @property
    def target_temp(self):
        
        return self._target_temp
    
    @property
    def mode(self):
        
        return self._mode
    
    @property
    def fan_speed(self):
        
        return self._fan_speed
    
    @property
    def _current_temp(self):
        self.update_state()
        return self.current_temp
    
    @property
    def _humidity(self):
        self.update_state()
        return self.humidity
    
    # 控制功能
    def turn_on(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("climate","turn_on",payload)
        self.update_state()
        return f"空调开机命令发送{'成功' if res.status_code==200 else '失败'}"
    
    def turn_off(self):
        payload = {"entity_id": self.entity_id}
        res = self.set_property("climate","turn_off",payload)
        self.update_state()
        return f"空调关机命令发送{'成功' if res.status_code==200 else '失败'}"
    
    def set_temperature(self, temperature):
        payload = {"entity_id": self.entity_id,"temperature":temperature}
        res = self.set_property("climate","set_temperature",payload)
        self.update_state()
        return f"空调设置温度为{temperature}°C{'成功' if res.status_code==200 else '失败'}"
    
    def set_mode(self, mode):
        # 检查模式是否受支持
        if mode not in ['auto', 'off', 'heat', 'fan_only', 'cool']:
            e = f"错误：不支持的模式 '{mode}'。支持的模式有：{', '.join(['auto', 'off', 'heat', 'fan_only', 'cool'])}"
            print(e)
            return e
        payload = {"entity_id": self.entity_id,"hvac_mode":mode}
        res = self.set_property("climate","set_hvac_mode",payload)
        self.update_state()
        return f"空调设置模式为{mode}{'成功' if res.status_code==200 else '失败'}"
    
    def set_fan_speed(self, speed_level):
        # 检查模式是否受支持
        if speed_level not in ['Auto', 'Low', 'Medium', 'High']:
            e = f"错误：不支持的风速 '{speed_level}'。支持的风速有：{', '.join(['Auto', 'Low', 'Medium', 'High'])}"
            print(e)
            return e
        payload = {"entity_id": self.entity_id,"fan_mode":speed_level}
        res = self.set_property("climate","set_fan_mode",payload)
        self.update_state()
        return f"空调设置风速为{speed_level}{'成功' if res.status_code==200 else '失败'}"

    
# if __name__ == "__main__":
#     HA_URL = "http://192.168.0.18:8123"
#     ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
#     ENTITY_ID = "climate.giot_v1itcw_8957_thermostat"

#     ac = AirConditioner(HA_URL, ACCESS_TOKEN, ENTITY_ID)
#     # # 打印当前状态
#     # print("当前状态:")
#     # print(f"电源: {'开启' if ac.power_status else '关闭'}")
#     # print(f"模式: {ac.mode}")
#     # print(f"目标温度: {ac.target_temp}°C")
#     # print(f"当前温度: {ac.current_temp}°C")
#     # print(f"风速等级: {ac.fan_speed}")
#     # print(f"湿度: {ac.humidity}%")

    
#     res = ac.set_temperature(19)
#     print(res.status_code)
#     # ac.set_mode('cool')
#     # ac.set_fan_speed('Low')
    
#     # res = ac.get_property()
#     # print(res)
    