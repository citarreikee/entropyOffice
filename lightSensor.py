from datetime import datetime
# from contextlib import contextmanager
# import datetime as dt
import time
from typing import Callable, Dict, Any, List, Optional


class VirtualLightSensor:
    """
    增强型虚拟光敏传感器 - 内置灯具状态感知能力
    特性：
    1. 自动关联灯具对象列表
    2. 实时统计开启灯具数量
    3. 动态计算综合光照强度（1-5级）
    """
    
    def __init__(self, lights=None, sensor_id="virtual_light_sensor"):
        """
        :param lights: 灯具对象列表（需实现status属性）
        :param sensor_id: 传感器标识
        """
        self.tools = {
                    "type": "function",
                    "function": {
                        "name": "get_illuminance",
                        "description": "获取虚拟光敏传感器的当前光照强度（1-5级）",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "sensor_id": {
                            "type": "string",
                            "description": "虚拟传感器的标识符 (默认: virtual_light_sensor)"
                            }
                        },
                        "required": []
                        }
                    }
                    }
        self.sensor_id = sensor_id
        self.lights = lights or []  # 灯具对象列表
        self._final_illuminance = 3   # 初始光照值
        self._last_illuminance = None  # 记录上一次的光照值
        self._last_update = 0  # 上次更新时间戳
        # 事件系统
        self._event_handlers = {
            "illuminance_change": []   # 光照变化事件
        }
        
        
    def _calculate_base_illuminance(self):
        """计算时间基础光照值（6:00=1 → 12:00=5 → 18:00=1）"""
        now = datetime.now().time()
        hour = now.hour + now.minute/60
        
        # 时间分段计算光照基准值
        if 6 <= hour < 12:  # 6:00-12:00 线性上升
            return 1 + min(4, (hour - 6) * 4/6)
        elif 12 <= hour < 18:  # 12:00-18:00 线性下降
            return 5 - min(4, (hour - 12) * 4/6)
        else:  # 夜间恒定1
            return 1

    def _count_active_lights(self):
        """统计开启的灯具数量（自动感知灯具状态）"""
        return sum(1 for light in self.lights if light.status == "on")
    
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
            "sensor_id": self.sensor_id,
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event_data["timestamp"]))
        }
        full_data.update(event_data)
        
        for handler in self._event_handlers[event_type]:
            try:
                handler(full_data)
            except Exception as e:
                print(f"Error in event handler: {e}")
    

    def update_illuminance(self):
        """获取综合光照强度（基础值 + 灯具叠加）并检测变化"""
        base_value = self._calculate_base_illuminance()
        active_lights = self._count_active_lights()
        
        # 每盏灯增加1级强度（上限5）
        new_illuminance = min(5, base_value + active_lights)
        
        # 检测光照变化（变化量≥0.5时触发事件）
        if self._last_illuminance is not None and abs(new_illuminance - self._last_illuminance) >= 0.5:
            self._trigger_event("illuminance_change", {
                "old_illuminance": self._last_illuminance,
                "new_illuminance": new_illuminance,
                "delta": round(new_illuminance - self._last_illuminance, 1),
                "timestamp": time.time()
            })
        
        # 更新状态
        self._last_illuminance = new_illuminance
        self._final_illuminance = new_illuminance
        self._last_update = time.time()
        return True
    
    # 实时光照强度查询
    @property
    def final_illuminance(self):
        # 如果超过1分钟未更新，则强制更新
        if time.time() - self._last_update > 60:
            self.update_illuminance()
        return self._final_illuminance

    def get_illuminance(self):
        """获取当前的光照强度"""
        return self.final_illuminance
# ================= 使用示例 =================
# if __name__ == "__main__":
#     # 1. 灯具类定义（需实现status属性）
#     class SmartLight:
#         def __init__(self, light_id):
#             self.light_id = light_id
#             self.status = "off"
        
#         def turn_on(self):
#             self.status = "on"
#             print(f"💡 {self.light_id} 已开启")
        
#         def turn_off(self):
#             self.status = "off"
#             print(f"💡 {self.light_id} 已关闭")
    
#     # 2. 初始化传感器
#     print("="*50)
#     print("🌞 虚拟光敏传感器系统启动")
#     print("="*50)
    
#     # 创建3盏灯具
#     light1 = SmartLight("客厅主灯")
#     light2 = SmartLight("书房台灯")
#     light3 = SmartLight("卧室夜灯")
    
#     # 初始化传感器
#     sensor = VirtualLightSensor(
#         lights=[light1, light2, light3],
#         sensor_id="office_sensor"
#     )
    
#     # 3. 修复时间模拟函数（核心修复点）
#     @contextmanager
#     def simulate_time(hour, minute):
#         """时间作用域锁定器"""
#         class MockDateTime(dt.datetime):
#             @classmethod
#             def now(cls):
#                 return cls(2023, 1, 1, hour, minute)
        
#         # 进入作用域时覆盖全局datetime
#         original_datetime = __import__('datetime').datetime
#         __import__('datetime').datetime = MockDateTime
        
#         try:
#             yield  # 在此范围内时间被锁定
#         finally:
#             __import__('datetime').datetime = original_datetime  # 退出时恢复
    
#     # 4. 主演示流程
#     # 场景1：早晨8:30（预期基础光照≈2.7级）
#     simulate_time(8, 30)  
#     light1.turn_on()
#     light2.turn_on()
    
#     # 获取早晨状态
#     print("\n🌅 早晨工作场景:")
#     report = sensor.get_status_report()
#     print(f"📊 基础光照: {report['base_illuminance']:.1f}级 | "
#           f"开启灯具: {report['active_lights']}盏 | "
#           f"总强度: {report['final_illuminance']}级")  # 预期：基础≈2.7 + 2灯 = 4.7级（上限5）
    
#     # 场景2：中午12:00（预期基础光照5级）
#     simulate_time(12, 0)  
#     light1.turn_off()
#     light2.turn_off()
    
#     print("\n☀️ 中午自然光照场景:")
#     report = sensor.get_status_report()
#     print(f"📊 基础光照: {report['base_illuminance']:.1f}级 | "
#           f"开启灯具: {report['active_lights']}盏 | "
#           f"总强度: {report['final_illuminance']}级")  # 预期：5级
    
#     # 场景3：夜间21:00（预期基础光照1级）
#     simulate_time(21, 0)  
#     light3.turn_on()
    
#     print("\n🌙 夜间休息场景:")
#     report = sensor.get_status_report()
#     print(f"📊 基础光照: {report['base_illuminance']:.1f}级 | "
#           f"开启灯具: {report['active_lights']}盏 | "
#           f"总强度: {report['final_illuminance']}级")  # 预期：1 + 1灯 = 2级
    
#     # # 5. 动态添加灯具
#     # print("\n➕ 动态添加新灯具")
#     # light4 = SmartLight("阳台景观灯")
#     # sensor.add_light(light4)
#     # light4.turn_on()
    
#     # 最终状态报告
#     print("\n📝 最终状态报告:")
#     report = sensor.get_status_report()
#     for key, value in report.items():
#         print(f"{key.replace('_', ' ').title()}: {value}")
    
#     print("\n" + "="*50)
#     print("✅ 系统演示完成")
#     print("="*50)
#     print(sensor._calculate_base_illuminance())