from config import *
from tools import tools
from func_call import parse_function_call
import auto_inputer
import asyncio

from ollama import chat, Message, Client

client = Client(host=OLLAMA_URL)

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
            MODEL, 
            messages=conversation_history,
            tools=tools
        )
        
        # 检查是否需要继续处理
        if not response.message.get('tool_calls'):
            return response.message
        
# 重构的主聊天函数
async def main_chat():
    """主聊天循环 - 完全重构版"""
    # 初始化对话历史
    conversation_history = [
        {
            "role": "system", 
            "content": """
            #人物设定
            你是JOJO办公室的智能设备管家，自主调用场景中的设备来营造良好的办公环境

            # 场景设定            
            光照强度传感器在JOJO桌面上，光照强度有5档，从1到5逐渐变亮
            显示器挂灯在JOJO的显示器上
            温湿度传感器编号对应关系{1: jojo办公桌, 2: 办公室中段,3: 门口走廊}
            办公室灯组编号对应关系{1: 主照明灯, 2: 补光辅灯,3: 走廊灯}
            空调对应关系{1:办公室西侧空调（jojo旁边）, 2: 办公室中段空调}
            办公室的员工有JOJO、Chill1、Shang

            # 设备库
            照明：主灯、辅灯、走廊灯、显示器挂灯
            空调：办公室西侧空调、办公室中段空调
            小爱智能音箱
            WiFi路由器
            传感器：温湿度传感器*3
            

            # 运行经验
            4档是最适合办公的光照强度；
            如果Chill1、JOJO、Shang这三人之中至少一人在，就应该保持合适的办公环境;
            走廊灯除非命令打开，否则一般不主动开，也不影响办公室亮度；
            可以通过查询Wifi连接的方式判断办公室有谁在，他们的手机型号分别是{Chill1: SamsungGalaxyS21ultra，JOJO: Xiaomi14，Shang: iPhoneXR}；
            如果没人在，需要关闭所有电器
            办公室空调是中央水冷空调，一般需要调到15°C降温效果才明显
            可以通过小爱智能音箱播放一些需要的内容
            
            """
        }
    ]
    
    print("智能办公室控制系统已启动。输入'exit'退出。")
    

    while True:
        
        
        # 1. 优先处理待处理事件（最高优先级）
        if not auto_inputer.event_queue.empty():
            # 获取事件并更新最后事件时间
            event_message = auto_inputer.event_queue.get()
            
            
            print(f"\n[系统通知] {event_message['content']}")
            conversation_history.append(event_message)
            
            # 调用模型获取初始响应
            response = client.chat(MODEL, messages=conversation_history, tools=tools)
            # 处理工具调用链
            final_message = await process_tool_calls(response, conversation_history)

            # 更新对话历史
            conversation_history.append(final_message)
            
            # 输出响应
                    
            if final_message.get('content'):
                print(f"\n智能助理: {final_message['content']}")            
            
            
            continue              
        
        

if __name__ == "__main__":
    # 运行主聊天循环
    asyncio.run(main_chat())