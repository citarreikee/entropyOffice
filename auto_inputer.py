from devices import *

import queue
import threading
import time
import datetime  # 添加 datetime 模块用于时间格式化

# 创建全局事件队列
event_queue = queue.Queue()

# 时间格式化函数
def format_timestamp(timestamp):
    """将时间戳转换为易读的日期时间格式"""
    return datetime.datetime.fromtimestamp(timestamp).strftime("%m-%d %H:%M:%S")

# 改进的传感器事件处理函数
# 传感器映射
sensor_map = {
    "button.miaomiaoce_t2_ceca_info": "sensor1",
    "button.miaomiaoce_t2_58bc_info": "sensor2",
    "button.miaomiaoce_t2_faed_info": "sensor3",
    }
def sensor_event_handler(event_data: dict) -> None:
    """处理温湿度计事件并将其加入队列 - 改进版"""
    entity_id = sensor_map[event_data['entity_id']]
    event_type = event_data['event_type']
    timestamp = format_timestamp(event_data['timestamp'])  # 使用格式化时间
    
    if event_type == "temp_change":
        message = (f"{timestamp}⚠️ 温度变化通知：{entity_id} 温度变化 {event_data['delta']:.1f}°C "
                   f"({event_data['old_temp']:.1f}℃ → {event_data['new_temp']:.1f}℃)")
    elif event_type == "humidity_change":
        message = (f"{timestamp}⚠️ 湿度变化通知：{entity_id} 湿度变化 {event_data['delta']:.1f}% "
                   f"({event_data['old_humidity']:.1f}% → {event_data['new_humidity']:.1f}%)")
    else:
        return
    
    # 将事件放入队列 - 添加时间戳确保顺序
    event_queue.put({
        "timestamp": time.time(),
        "role": "user", 
        "content": message
    })

# 新增路由器事件处理函数
def router_event_handler(event_data: dict) -> None:
    """处理路由器设备变化事件"""
    device = event_data['device']
    event_type = event_data['event_type']
    timestamp = format_timestamp(event_data['timestamp'])  # 使用格式化时间
    
    if event_type == "device_online":
        message = f"{timestamp}📱 设备上线通知：{device} 已连接到网络 (IP: {event_data['ip']})"
    elif event_type == "device_offline":
        message = f"{timestamp}📴 设备离线通知：{device} 已断开网络连接"
    else:
        return
    
    # 将事件放入队列
    event_queue.put({
        "timestamp": time.time(),
        "role": "user", 
        "content": message
    })

# 注册事件处理器
th_sensor1.register_event_handler("temp_change", sensor_event_handler)
th_sensor1.register_event_handler("humidity_change", sensor_event_handler)
th_sensor2.register_event_handler("temp_change", sensor_event_handler)
th_sensor2.register_event_handler("humidity_change", sensor_event_handler)
th_sensor3.register_event_handler("temp_change", sensor_event_handler)
th_sensor3.register_event_handler("humidity_change", sensor_event_handler)
router.register_event_handler("device_online", router_event_handler)
router.register_event_handler("device_offline", router_event_handler)

# # 启动温湿度计监控线程
# def sensor_monitor():
#     """后台监控温湿度计"""
#     while True:
#         try:
#             th_sensor1.update_state()
#             th_sensor2.update_state()
#             th_sensor3.update_state()
#             time.sleep(10)  # 每10秒检查一次
#         except Exception as e:
#             print(f"温湿度监控异常: {e}")

# 新增路由器监控线程
def router_monitor():
    """后台监控路由器设备状态"""
    while True:
        try:
            router.update_state()
            time.sleep(30)  # 每30秒检查一次
        except Exception as e:
            print(f"路由器监控异常: {e}")




# sensor_thread = threading.Thread(target=sensor_monitor, daemon=True)
# sensor_thread.start()

router_thread = threading.Thread(target=router_monitor, daemon=True)
router_thread.start()

