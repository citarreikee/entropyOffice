import subprocess
import platform
import time

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
            "DESKTOP-S9174ND": "192.168.31.44",
            "LaptopZQ": "192.168.31.40",
            "iPhoneXR": "192.168.31.76",
            "Mac-mini": "192.168.31.10"
        }
        self.max_retries = max_retries  # 最大重试次数
        self.timeout = timeout          # 超时时间(秒)
        self.last_update = 0
        self.cache_duration = 60        # 缓存有效期(秒)
        self._online_devices = []

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

    def update_state(self):
        """更新在线设备状态(带缓存机制)"""
        # 检查缓存有效期
        if time.time() - self.last_update < self.cache_duration:
            return True
        
        new_status = {}
        for device, ip in self.device_map.items():
            new_status[device] = self.ping_device(ip)
        
        self._online_devices = [d for d, online in new_status.items() if online]
        self.last_update = time.time()
        return True

    @property
    def online_devices(self):
        """带缓存的在线设备查询"""
        self.update_state()
        return self._online_devices


if __name__ == "__main__":
    router = WifiRouter()
    print("当前在线设备：", router.online_devices)





