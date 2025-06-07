"""An agent implemented by assistant with qwen3"""
import os  # noqa

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print

import json
import requests

from devices import screenlamp, wifispeaker, officelight

@register_tool('screen_light')
class Screen_light(BaseTool):
    # The `description` tells the agent the functionality of this tool.
    description = '显示器挂灯服务，可以查看开关状态和控制灯的开关'
    # The `parameters` tell the agent what input parameters the tool has.
    parameters = [{
        'name': 'operate',
        'type': 'string',
        'description': '操作类型，可选项为["get"，"put"]之一，分别为查询灯的状态、控制灯的开关',
        'required': True
    },  
    {
        'name': 'value',
        'type': 'string',
        'description': '"operate"参数为"put"时传参，可选项为["0"，"1"]之一,分别为关灯和开灯'
    }]

    def __init__(self, cfg = None):
        super().__init__(cfg)
        self.status = 0
    
    def call(self, params, **kwargs):
        
        params = self._verify_json_format_args(params)
        operate = params['operate']
        if operate == 'get':
            return self.status
        elif operate == 'put':
            value = params['value']
            self.status = int(value)
            if self.status == 1:
                screenlamp.turn_on()
            elif self.status == 0:
                screenlamp.turn_off()

            return "命令已发送"
        
        return super().call(params, **kwargs)
    
@register_tool('main_light')
class Main_light(BaseTool):
    # The `description` tells the agent the functionality of this tool.
    description = '办公室主灯服务，可以查看开关状态和控制灯的开关'
    # The `parameters` tell the agent what input parameters the tool has.
    parameters = [{
        'name': 'operate',
        'type': 'string',
        'description': '操作类型，可选项为["get"，"put"]之一，分别为查询灯的状态、控制灯的开关',
        'required': True
    },  
    {
        'name': 'value',
        'type': 'string',
        'description': '"operate"参数为"put"时传参，可选项为["0"，"1"]之一,分别为关灯和开灯'
    }]

    def __init__(self, cfg = None):
        super().__init__(cfg)
        self.status = 1
    
    def call(self, params, **kwargs):
        params = self._verify_json_format_args(params)
        operate = params['operate']
        if operate == 'get':
            return self.status
        elif operate == 'put':
            value = params['value']
            self.status = int(value)
            if self.status == 0:
                res = officelight.main_turn_off()
            elif self.status == 1:
                res = officelight.main_turn_on()

            return str(res)
        
        # return super().call(params, **kwargs)
    
@register_tool('corridor_light')
class Corridor_light(BaseTool):
    # The `description` tells the agent the functionality of this tool.
    description = '办公室走廊灯服务，可以查看开关状态和控制灯的开关'
    # The `parameters` tell the agent what input parameters the tool has.
    parameters = [{
        'name': 'operate',
        'type': 'string',
        'description': '操作类型，可选项为["get"，"put"]之一，分别为查询灯的状态、控制灯的开关',
        'required': True
    },  
    {
        'name': 'value',
        'type': 'string',
        'description': '"operate"参数为"put"时传参，可选项为["0"，"1"]之一,分别为关灯和开灯'
    }]

    def __init__(self, cfg = None):
        super().__init__(cfg)
        self.status = 0
    
    def call(self, params, **kwargs):
        params = self._verify_json_format_args(params)
        operate = params['operate']
        if operate == 'get':
            return self.status
        elif operate == 'put':
            value = params['value']
            self.status = int(value)
            if self.status == 0:
                res = officelight.corridor_turn_off()
            elif self.status == 1:
                res = officelight.corridor_turn_on()

            return str(res)
        
        return super().call(params, **kwargs)
    
@register_tool('side_light')
class Side_light(BaseTool):
    # The `description` tells the agent the functionality of this tool.
    description = '办公室辅灯服务，可以查看开关状态和控制灯的开关'
    # The `parameters` tell the agent what input parameters the tool has.
    parameters = [{
        'name': 'operate',
        'type': 'string',
        'description': '操作类型，可选项为["get"，"put"]之一，分别为查询灯的状态、控制灯的开关',
        'required': True
    },  
    {
        'name': 'value',
        'type': 'string',
        'description': '"operate"参数为"put"时传参，可选项为["0"，"1"]之一,分别为关灯和开灯'
    }]

    def __init__(self, cfg = None):
        super().__init__(cfg)
        self.status = 0
    
    def call(self, params, **kwargs):
        params = self._verify_json_format_args(params)
        operate = params['operate']
        if operate == 'get':
            return self.status
        elif operate == 'put':
            value = params['value']
            self.status = int(value)
            if self.status == 0:
                res = officelight.side_turn_off()
            elif self.status == 1:
                res = officelight.side_turn_on()

            return str(res)
        
        return super().call(params, **kwargs)
    
@register_tool('wifi_connect_phones')
class WifiConnectSearch(BaseTool):
    description = '这是一个查询当前连接到wifi的手机型号的服务，它会返回一个列表，包含当前连接到wifi的所有手机的型号'
    parameters = []
    def call(self, params, **kwargs):
        params = self._verify_json_format_args(params)
        return ["SamsungGalaxyS21ultra", "Xiaomi14", "iphone13"]


@register_tool('search_light_force')
class SearchLightForce(BaseTool):
    description = '这是一个查询当前光照强度的服务，会返回当前光照强度'
    parameters = []

    def __init__(self, cfg = None):
        super().__init__(cfg)
        self.count = 0

    def call(self, params, **kwargs):
        params = self._verify_json_format_args(params)
        self.count += 1
        if self.count < 3:
            return self.count
        if self.count >= 3:
            return 4






def init_agent_service():
   
    llm_cfg = {
        # Use your own model service compatible with OpenAI API by vLLM/SGLang:
        'model': 'qwen3:30b-a3b',
        'model_server': 'http://localhost:11434/v1',  # api_base
        'api_key': 'EMPTY',
    
        'generate_cfg': {
            # When using vLLM/SGLang OAI API, pass the parameter of whether to enable thinking mode in this way
            'extra_body': {
                'chat_template_kwargs': {'enable_thinking': False}
            },
    
            # Add: When the content is `<think>this is the thought</think>this is the answer`
            # Do not add: When the response has been separated by reasoning_content and content
            # This parameter will affect the parsing strategy of tool call
            # 'thought_in_content': True,
        },
    }
    tools = [
        # {
        #     'mcpServers': {  # You can specify the MCP configuration file
        #         'time': {
        #             'command': 'uvx',
        #             'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
        #         }
        #     }
        # },
        # pip install "qwen-agent[code_interpreter]"
        # 'code_interpreter',  # Built-in tools
        'screen_light',
        'main_light',
        'side_light',
        'corridor_light',
        'wifi_connect_phones',
        'search_light_force'        
    ]
    bot = Assistant(llm=llm_cfg,
                    function_list=tools,
                    files=["./mvp.md"],
                    # system_message = '''After receiving the user's request, you should:
                    #                         - first read Yeelink.md to learn about APIs,
                    #                         - then generate code to meet user's requirements,
                    #                         - and run code with code_interpreter.
                    #                         Please show the result of your callings.'''
                    system_message = '''你是办公室智能设备管理助手，当你收到输入的时候，你应该：
                                        - 判断一下当前输入信号是否关系到你需要做出任何调整，
                                        - 查询所有设备的状态来整体理解办公室的环境状态，
                                        - 结合场景设定、场景知识和过往运行经验总结制定你的解决方案，
                                        - 调用相应的工具执行你的解决方案，
                                        - 最后再次查询一下光照传感器，确保办公室环境状态已经调整至最佳
                                        - 向用户说明你做出的调整
                                            '''
                    )

    return bot


def app_tui():
    # Define the agent
    bot = init_agent_service()

    # Chat
    messages = []

    while True:
        query = input('\nuser:')
        print(query)
       
        messages.append({'role': 'user', 'content': query})
        response = []
        response_plain_text = ''
        for response in bot.run(messages=messages):
            response_plain_text = typewriter_print(response, response_plain_text)
        messages.extend(response)





if __name__ == '__main__':
    
    app_tui()
