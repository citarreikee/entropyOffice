from . import config
from . import yeelinkLamp22Cad9Light
from . import mengliLamp
from . import wifiSpeaker
from . import officeLight


screenlamp = yeelinkLamp22Cad9Light.YeelinkLamp22Cad9Light(config.HOME_ASSISTANT_TOKEN)
lamp001 = mengliLamp.MengliLamp001(config.DEVICE_ADDRESS,config.CHARACTERISTIC_UUID_W,config.CHARACTERISTIC_UUID_R)
officelight = officeLight.OfficeLight(config.HOME_ASSISTANT_TOKEN) 
speaker = wifiSpeaker.WifiSpaekerlx06(config.HOME_ASSISTANT_TOKEN)



# from config import HOME_ASSISTANT_TOKEN
# from yeelinkLamp22Cad9Light import YeelinkLamp22Cad9Light

# lamp = YeelinkLamp22Cad9Light(HOME_ASSISTANT_TOKEN)

