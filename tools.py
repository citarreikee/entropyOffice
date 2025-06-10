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
                "description": "要控制的空调编号",
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
    },
    {
        "type": "function",
        "function": {
            "name": "OfficeLightControl",
            "description": "控制和查询办公室基础灯光",
            "parameters": {
            "type": "object",
            "properties": {
                "lightID": {
                "type": "integer",
                "description": "要操作的灯组编号",
                },                
            },
            "action": {
                "type": "string",
                "description": "要执行的操作类型，从以下枚举值中选其一",
                "enum": ["turn_on", "turn_off", "query_status"]
                },
            "required": ["lightID","action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "TH_SensorQuery",
            "description": "查询温湿度计的读数",
            "parameters": {
            "type": "object",
            "properties": {
                "thID": {
                "type": "integer",
                "description": "要查询的温湿度计编号",
                },                
            },  
            "required": ["thID"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "SpeakerControl",
            "description": "控制音箱播放特定的内容",
            "parameters": {
            "type": "object",
            "properties": {
                "text": {
                "type": "string",
                "description": "要播放的文字内容，简短连续，不能有特殊符号"
                }
            },
            "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ScreenLightControl",
            "description": "控制显示器挂灯，支持开关、调节亮度、调节色温和状态查询功能",
            "parameters": {
            "type": "object",
            "properties": {
                "action": {
                "type": "string",
                "description": "要执行的操作类型，从以下枚举值中选其一",
                "enum": ["turn_on", "turn_off", "set_brightness", "set_color_temp", "query_status"]
                },
                "brightness": {
                "type": "number",
                "description": "亮度，范围:1~100，步长: 1，仅当action为set_brightness时使用",
                },
                "color_temp": {
                "type": "number",
                "description": "色温，范围:2700~6500，步长: 1，仅当action为set_color_temp时使用",
                },
            },
            "required": ["action"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "RouterQuery",
            "description": "查询路由器在线的设备，返回在线设备列表",
            "parameters": {
            "type": "object",
            "properties": { },
        "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_illuminance",
            "description": "获取光敏传感器的当前光照强度（1-5级）",
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
]