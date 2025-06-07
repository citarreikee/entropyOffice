import dashscope
from dashscope import Generation
import json
import asyncio
import warnings
from airConditioner import AirConditioner
import ssl
from TH_Sensor import TH_Sensor

import time
import sys

import queue
import threading

from ollama import chat, Message, Client

# ... 其他配置保持不变 ...
OLLAMA_URL = "http://localhost:11434/"
HA_URL = "http://192.168.0.18:8123"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2OTFhNWNjMThlOTM0MmI2OTdmNTVlNGZmNmEwYThlYiIsImlhdCI6MTc0ODg0OTQyMiwiZXhwIjoyMDY0MjA5NDIyfQ.1HTLOmqphNp2Mv--Krj_nvNHkjhWAGCgQ2CztKd4sx8"
ENTITY_ID1 = "climate.giot_v1itcw_8957_thermostat"
ENTITY_ID2 = "climate.fawad_3010_ea3a_air_conditioner"

client = Client(host=OLLAMA_URL)

# 假设已配置好HA_URL和TOKEN
ac1 = AirConditioner(HA_URL, ACCESS_TOKEN, ENTITY_ID1)
ac2 = AirConditioner(HA_URL, ACCESS_TOKEN, ENTITY_ID2)



# 空调ID映射
ac_map = {
    1: ac1,
    2: ac2,
    }

# 工具定义
tools = [
    {
  "type": "function",
  "function": {
    "name": "AirConditionerControl",
    "description": "控制办公室空调系统，支持开关机、温度调节、模式选择、风速设置和状态查询功能",
    "parameters": {
      "type": "object",
      "properties": {
        "acID": {
          "type": "integer",
          "description": "要控制的空调编号（1-jojo旁边的空调, 2-门口空调）",
          "enum": [1, 2, 3]
        },
        "action": {
          "type": "string",
          "description": "要执行的操作类型，从以下枚举值中选其一",
          "enum": ["turn_on", "turn_off", "set_temperature", "set_mode", "set_fan_speed", "query_status"]
        },
        "temperature": {
          "type": "number",
          "description": "目标温度值（摄氏度），仅当action为set_temperature时使用",
          "minimum": 16,
          "maximum": 30
        },
        "mode": {
          "type": "string",
          "description": "工作模式，仅当action为set_mode时使用",
          "enum": ["auto", "heat", "cool", "fan_only"]
        },
        "fan_speed": {
          "type": "string",
          "description": "风速等级，仅当action为set_fan_speed时使用",
          "enum": ["Auto", "Low", "Medium", "High"]
        }
      },
      "required": ["acID", "action"],
      
    }
  }
}
]

async def parse_function_call(model_response, messages):
    """解析并执行所有函数调用 - 支持递归处理多级工具调用"""
    if not model_response.message.get('tool_calls'):
        return None
    
    tool_calls = model_response.message['tool_calls']
    tool_responses = []
    
    # 处理所有工具调用
    for tool_call in tool_calls:
        func_name = tool_call['function']['name']
        args = tool_call['function']['arguments']
        
        try:
            if func_name == "AirConditionerControl":
                ac_id = args.get("acID")
                action = args.get("action")
                
                if not ac_id or ac_id not in [1, 2]:
                    response_content = "错误：缺少或无效的空调ID (请使用1,2)"
                elif not action:
                    response_content = "错误：缺少操作类型(action)"
                else:
                    ac = ac_map.get(ac_id)
                    if not ac:
                        response_content = f"错误：找不到ID为{ac_id}的空调"
                    else:
                        try:
                            if action == "turn_on":
                                result = ac.turn_on()
                                response_content = result
                                
                            elif action == "turn_off":
                                result = ac.turn_off()
                                response_content = result
                                
                            elif action == "set_temperature":
                                temp = args.get("temperature")
                                if temp is None:
                                    response_content = "错误：温度设置需要temperature参数"
                                else:
                                    result = ac.set_temperature(temp)
                                    response_content = result
                                    
                            elif action == "set_mode":
                                mode = args.get("mode")
                                if mode is None:
                                    response_content = "错误：模式设置需要mode参数"
                                else:
                                    result = ac.set_mode(mode)
                                    response_content = result
                                    
                            elif action == "set_fan_speed":
                                fan_speed = args.get("fan_speed")
                                if fan_speed is None:
                                    response_content = "错误：风速设置需要fan_speed参数"
                                else:
                                    result = ac.set_fan_speed(fan_speed)
                                    response_content = result

                            elif action == "query_status":
                                # 查询空调状态
                                ac.update_state()  # 确保获取最新状态
                                status = (
                                    f"空调{ac_id}状态:\n"
                                    f"• 开关状态: {'开启' if ac.power_status else '关闭'}\n"
                                    f"• 当前温度: {ac.current_temp}°C\n"
                                    f"• 目标温度: {ac.target_temp}°C\n"
                                    f"• 当前湿度: {ac.humidity}%\n"
                                    f"• 工作模式: {ac.mode}\n"
                                    f"• 风速等级: {ac.fan_speed}"
                                )
                                response_content = status
                                       
                            else:
                                response_content = f"错误：未知操作类型 '{action}'。支持的操作有：{', '.join(['turn_on', 'turn_off', 'set_temperature', 'set_mode', 'set_fan_speed', 'query_status'])}"
                                                                
                        except Exception as e:
                            response_content = f"空调控制出错: {str(e)}"
                
                tool_responses.append({
                    "tool_call_id": tool_call,
                    "role": "tool",
                    "name": func_name,
                    "content": response_content
                })
                print({
                    "tool_call_id": tool_call,
                    "role": "tool",
                    "name": func_name,
                    "content": response_content
                })
                
            else:
                tool_responses.append({
                    "tool_call_id": tool_call,
                    "role": "tool",
                    "name": func_name,
                    "content": f"未知函数调用: {func_name}"
                })
                
        except Exception as e:
            tool_responses.append({
                "tool_call_id": tool_call,
                "role": "tool",
                "name": func_name,
                "content": f"执行异常: {str(e)}"
            })
    
        
    # 添加所有工具响应到消息历史
    messages.extend(tool_responses)
    
    # 返回工具响应列表，而不是直接调用模型
    return tool_responses
    

async def process_tool_calls(response, conversation_history):
    """递归处理工具调用链 - 修复版"""
    while True:
        model_message = response.message
        
        # 如果没有工具调用，返回最终响应
        if not model_message.get('tool_calls'):
            return model_message
        
        # 添加当前模型消息到历史
        conversation_history.append(model_message)
        print(f"检测到{len(model_message['tool_calls'])}个工具调用，正在执行...")
        
        # 解析并执行工具调用
        tool_responses = await parse_function_call(response, conversation_history)
        if not tool_responses:
            return {"role": "assistant", "content": "工具调用处理失败"}
        
        # 使用工具响应再次调用模型
        response = client.chat(
            "qwen3:30b-a3b", 
            messages=conversation_history,
            tools=tools
        )
        
        # 检查是否需要继续处理
        if not response.message.get('tool_calls'):
            return response.message

# 创建温湿度计实例
sensor1 = TH_Sensor(HA_URL, ACCESS_TOKEN, "button.miaomiaoce_t2_ceca_info")
# sensor2 = TH_Sensor(HA_URL, ACCESS_TOKEN, "sensor.bedroom_temperature")     # 替换为实际的温湿度计ID

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
sensor1.register_event_handler("temp_change", sensor_event_handler)
sensor1.register_event_handler("humidity_change", sensor_event_handler)
# sensor2.register_event_handler("temp_change", sensor_event_handler)
# sensor2.register_event_handler("humidity_change", sensor_event_handler)

# 启动温湿度计监控线程
def sensor_monitor():
    """后台监控温湿度计"""
    while True:
        try:
            sensor1.update_state()
            # sensor2.update_state()
            time.sleep(10)  # 每10秒检查一次
        except Exception as e:
            print(f"温湿度监控异常: {e}")

sensor_thread = threading.Thread(target=sensor_monitor, daemon=True)
sensor_thread.start()

def display_status():
    """显示当前设备状态"""
    print(f"1号空调: {'开启' if ac1.power_status else '关闭'} | 温度: {ac1.current_temp}°C | 目标: {ac1.target_temp}°C")
    print(f"2号空调: {'开启' if ac2.power_status else '关闭'} | 温度: {ac2.current_temp}°C | 目标: {ac2.target_temp}°C")
    print(f"环境湿度: {sensor1.humidity}%")

# 重构的主聊天函数
async def main_chat():
    """主聊天循环 - 完全重构版"""
    # 初始化对话历史
    conversation_history = [
        {
            "role": "system", 
            "content": "你是智能楼宇设备控制管家，根据用户的需求和环境变化自动调整设备。"
        }
    ]
    
    print("智能空调控制系统已启动（支持温湿度事件触发）。输入'exit'退出。")
    
    # 状态初始化
    last_status_update = time.time()
    STATUS_UPDATE_INTERVAL = 60  # 每分钟更新一次状态显示
    last_input_prompt = 0
    INPUT_PROMPT_INTERVAL = 60  # 每20秒显示一次输入提示
    
    # 初始状态显示
    print("\n[系统] 初始设备状态:")
    display_status()
    
    # 使用更智能的提示系统
    print("\n您可以输入指令控制空调，例如：")
    print("  - '打开1号空调'")
    print("  - '设置1号空调到24度'")
    print("  - '关闭所有空调'")
    print("  - '当前状态'")
    print("如需帮助，请输入'help'")
    
    # 主循环标志
    active_input = False
    last_event_time = 0

    while True:
        
        
        # 1. 优先处理待处理事件（最高优先级）
        if not event_queue.empty():
            # 获取事件并更新最后事件时间
            event_message = event_queue.get()
            
            
            print(f"\n[系统通知] {event_message['content']}")
            conversation_history.append(event_message)
            
            # 调用模型获取初始响应
            response = client.chat("qwen3:30b-a3b", messages=conversation_history, tools=tools)
            # 处理工具调用链
            final_message = await process_tool_calls(response, conversation_history)

            # 更新对话历史
            conversation_history.append(final_message)
            
            # 输出响应
                    
            if final_message.get('content'):
                print(f"\n智能助理: {final_message['content']}")            
            
            # 事件处理后立即更新状态显示
            print("\n[系统] 事件处理后状态更新:")
            display_status()
            continue              
        
        

if __name__ == "__main__":
    # 运行主聊天循环
    asyncio.run(main_chat())