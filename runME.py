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
            return model_message,conversation_history
        
        # 添加当前模型消息到历史
        conversation_history.append(model_message)
        print(f"检测到{len(model_message['tool_calls'])}个工具调用，正在执行...")
        
        # 解析并执行工具调用
        tool_responses,conversation_history = await parse_function_call(response, conversation_history)
        if not tool_responses:
            return {"role": "assistant", "content": "工具调用处理失败"},conversation_history
        
        # 使用工具响应再次调用模型
        response = client.chat(
            MODEL, 
            messages=conversation_history,
            tools=tools
        )
        conversation_history.append(response.message)
        
        # 检查是否需要继续处理
        if not response.message.get('tool_calls'):
            return response.message, conversation_history
        
# 重构的主聊天函数
async def main_chat():
    """主聊天循环 - 完全重构版"""
    # 初始化对话历史
    conversation_history = [
        {
            "role": "system", 
            "content": """
            # 人物设定
            你是JOJO办公室的智能设备管家，当收到任何输入，你应该：
            - 查询办公室人员、光照和温湿度情况，
            - 判断一下当前输入信号是否关系到你需要做出任何调整，也可能是无需干预，
            - 结合场景设定和过往运行经验制定你的解决方案，
            - 不需要向用户征求意见，直接执行

            # 场景设定            
            光敏传感器在JOJO桌面上
            显示器挂灯在JOJO的显示器上
            温湿度传感器编号对应关系{1: jojo办公桌, 2: 办公室中段,3: 门口走廊}
            办公室灯组编号对应关系{1: 主照明灯, 2: 补光辅灯,3: 走廊灯}
            空调对应关系{1:办公室西侧空调（jojo旁边）, 2: 办公室中段空调}
            办公室的同事有JOJO、Qi、Shang，手机型号分别是{Qi: SamsungGalaxyS21ultra，JOJO: Xiaomi14，Shang: iPhoneXR}
            

            # 运行经验
            可以用小爱智能音箱向用户汇报，向不同的人打招呼！
            查询光敏传感器，光照强度有5档，从1到5逐渐变亮，4是最适合办公的光照强度
            如果有人在办公室，就应该保持合适的办公环境；如果没人在，需要关闭所有电器
            可以通过查询Wifi连接的方式判断办公室有谁在
            JOJO在就开显示器灯              
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

            # 一点滑动窗口遗忘
            if len(conversation_history) > 5:
                conversation_history = [conversation_history[0]] + conversation_history[-2:]
            
            # 调用模型获取初始响应
            response = client.chat(MODEL, messages=conversation_history, tools=tools)
            # 处理工具调用链
            final_message,conversation_history = await process_tool_calls(response, conversation_history)

                        
            # 输出响应
                    
            if final_message.get('content'):
                print(f"\n智能助理: {final_message['content']}")            
            
            
            continue              
        
        

if __name__ == "__main__":
    # 运行主聊天循环
    asyncio.run(main_chat())