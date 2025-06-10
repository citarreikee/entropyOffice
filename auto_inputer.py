from devices import *

import queue
import threading
import time

# 创建全局事件队列
event_queue = queue.Queue()



# 改进的传感器事件处理函数
def sensor_event_handler(event_data: dict) -> None:
    """处理温湿度计事件并将其加入队列 - 改进版"""
    entity_id = event_data['entity_id']
    event_type = event_data['event_type']
    
    if event_type == "temp_change":
        message = (f"{time.time()}⚠️ 温度变化通知：{entity_id} 温度变化 {event_data['delta']:.1f}°C "
                   f"({event_data['old_temp']:.1f}℃ → {event_data['new_temp']:.1f}℃)")
    elif event_type == "humidity_change":
        message = (f"{time.time()}⚠️ 湿度变化通知：{entity_id} 湿度变化 {event_data['delta']:.1f}% "
                   f"({event_data['old_humidity']:.1f}% → {event_data['new_humidity']:.1f}%)")
    else:
        return
    
    # 将事件放入队列 - 添加时间戳确保顺序
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

# 启动温湿度计监控线程
def sensor_monitor():
    """后台监控温湿度计"""
    while True:
        try:
            th_sensor1.update_state()
            th_sensor2.update_state()
            th_sensor3.update_state()
            time.sleep(10)  # 每10秒检查一次
        except Exception as e:
            print(f"温湿度监控异常: {e}")

sensor_thread = threading.Thread(target=sensor_monitor, daemon=True)
sensor_thread.start()

while True:
        
        
        # 1. 优先处理待处理事件（最高优先级）
        if not event_queue.empty():
            # 获取事件并更新最后事件时间
            event_message = event_queue.get()
            
            
            print(f"\n[系统通知] {event_message['content']}")