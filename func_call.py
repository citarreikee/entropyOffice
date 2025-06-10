from devices import *
import asyncio


# 空调ID映射
ac_map = {
    1: ac1,
    2: ac2,
    }

# 办公室灯光映射
light_map = {
    1: main_light,
    2: aux_light,
    3: hallway_light,
}

# 传感器映射
sensor_map = {
    1: th_sensor1,
    2: th_sensor2,
    3: th_sensor3
}

# 显示器挂灯映射
screen_light_map = {
    1: screen_light1
}



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
            # 办公室灯光控制
            elif func_name == "OfficeLightControl":
                light_id = args.get("lightID")
                action = args.get("action")
                
                if not light_id or light_id not in [1, 2, 3]:
                    response_content = "错误：缺少或无效的灯光ID (请使用1,2,3)"
                elif not action:
                    response_content = "错误：缺少操作类型(action)"
                else:
                    light = light_map.get(light_id)
                    if not light:
                        response_content = f"错误：找不到ID为{light_id}的灯光"
                    else:
                        try:
                            if action == "turn_on":
                                result = light.turn_on()
                                response_content = result
                                
                            elif action == "turn_off":
                                result = light.turn_off()
                                response_content = result
                                
                            elif action == "query_status":
                                light.update_state()
                                status = (
                                    f"灯光{light_id}状态:\n"
                                    f"• 开关状态: {'开启' if light.status == 'on' else '关闭'}\n"
                                )
                                response_content = status
                                       
                            else:
                                response_content = f"错误：未知操作类型 '{action}'。支持的操作有：{', '.join(['turn_on', 'turn_off', 'query_status'])}"
                                                                
                        except Exception as e:
                            response_content = f"灯光控制出错: {str(e)}"
                
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
            
            # 温湿度传感器查询
            elif func_name == "TH_SensorQuery":
                th_id = args.get("thID")
                
                if not th_id or th_id not in [1, 2, 3]:
                    response_content = "错误：缺少或无效的传感器ID (请使用1,2,3)"
                else:
                    sensor = sensor_map.get(th_id)
                    if not sensor:
                        response_content = f"错误：找不到ID为{th_id}的温湿度传感器"
                    else:
                        try:
                            sensor.update_state()
                            status = (
                                f"温湿度传感器{th_id}状态:\n"
                                f"• 当前温度: {sensor.current_temp}°C\n"
                                f"• 当前湿度: {sensor.humidity}%\n"
                            )
                            response_content = status
                        except Exception as e:
                            response_content = f"传感器查询出错: {str(e)}"
                
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
            
            # 音箱控制
            elif func_name == "SpeakerControl":
                text = args.get("text")
                
                if not text:
                    response_content = "错误：缺少播放文本内容"
                else:
                    try:
                        result = speaker.play_text(text)
                        response_content = result
                    except Exception as e:
                        response_content = f"音箱控制出错: {str(e)}"
                
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
            
            # 显示器挂灯控制
            elif func_name == "ScreenLightControl":
                action = args.get("action")
                screen_id = args.get("screenID", 1)  # 默认为1号挂灯
                
                if not action:
                    response_content = "错误：缺少操作类型(action)"
                else:
                    screen_light = screen_light_map.get(screen_id)
                    if not screen_light:
                        response_content = f"错误：找不到ID为{screen_id}的显示器挂灯"
                    else:
                        try:
                            if action == "turn_on":
                                result = screen_light.turn_on()
                                response_content = result
                                
                            elif action == "turn_off":
                                result = screen_light.turn_off()
                                response_content = result
                                
                            elif action == "set_brightness":
                                brightness = args.get("brightness")
                                if brightness is None:
                                    response_content = "错误：亮度设置需要brightness参数"
                                else:
                                    result = screen_light.set_light_brightness(brightness)
                                    response_content = result
                                    
                            elif action == "set_color_temp":
                                color_temp = args.get("color_temp")
                                if color_temp is None:
                                    response_content = "错误：色温设置需要color_temp参数"
                                else:
                                    result = screen_light.set_light_color_temperature(color_temp)
                                    response_content = result
                                    
                            elif action == "query_status":
                                screen_light.update_state()
                                status = (
                                    f"显示器挂灯{screen_id}状态:\n"
                                    f"• 开关状态: {'开启' if screen_light.status else '关闭'}\n"
                                    f"• 当前亮度: {screen_light.brightness}\n"
                                    f"• 当前色温: {screen_light.color_temperature}K\n"
                                )
                                response_content = status
                                       
                            else:
                                response_content = f"错误：未知操作类型 '{action}'。支持的操作有：{', '.join(['turn_on', 'turn_off', 'set_brightness', 'set_color_temp', 'query_status'])}"
                                                                
                        except Exception as e:
                            response_content = f"显示器挂灯控制出错: {str(e)}"
                
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

