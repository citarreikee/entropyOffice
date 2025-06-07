from config import HA_URL,ACCESS_TOKEN
from officeLight import OfficeLight
from airConditioner import AirConditioner
from th_Sensor import TH_Sensor
from wifiSpeaker import WifiSpaekerlx06
from yeelinkLamp22Cad9Light import YeelinkLamp22Cad9Light

# 初始化办公室基础照明
MAIN_LIGHT_ID = "switch.xiaomi_2wpro3_de32_middle_switch_service"
main_light = OfficeLight(HA_URL, ACCESS_TOKEN, MAIN_LIGHT_ID)

AUX_LIGHT_ID = "switch.xiaomi_2wpro3_de32_left_switch_service"
aux_light = OfficeLight(HA_URL, ACCESS_TOKEN, AUX_LIGHT_ID)

HALLWAY_LIGHT_ID = "switch.xiaomi_2wpro3_de32_right_switch_service"
hallway_light = OfficeLight(HA_URL, ACCESS_TOKEN, HALLWAY_LIGHT_ID)

# 初始化办公室空调
AC1_ID = "climate.giot_v1itcw_8957_thermostat"
ac1 = AirConditioner(HA_URL, ACCESS_TOKEN, AC1_ID)

AC2_ID = "climate.fawad_3010_ea3a_air_conditioner"
ac2 = AirConditioner(HA_URL, ACCESS_TOKEN, AC2_ID)

# 初始化办公室温湿度传感器
TH1_ID = "button.miaomiaoce_t2_ceca_info"
th_sensor1 = TH_Sensor(HA_URL, ACCESS_TOKEN, TH1_ID)

TH2_ID = "button.miaomiaoce_t2_58bc_info"
th_sensor2 = TH_Sensor(HA_URL, ACCESS_TOKEN, TH2_ID)

TH3_ID = "button.miaomiaoce_t2_faed_info"
th_sensor3 = TH_Sensor(HA_URL, ACCESS_TOKEN, TH3_ID)

# 初始化语音播放扬声器
SPEAKER_ID = "text.xiaomi_lx06_c3ba_play_text"
speaker = WifiSpaekerlx06(HA_URL, ACCESS_TOKEN,SPEAKER_ID)

# 初始化显示器挂灯
Y1_LAMP_ID = "light.yeelink_lamp22_cad9_light"
screen_light1 = YeelinkLamp22Cad9Light(HA_URL, ACCESS_TOKEN,Y1_LAMP_ID)

