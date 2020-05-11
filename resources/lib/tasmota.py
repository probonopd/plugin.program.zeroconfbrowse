# To see the log:
#  cat ~/.kodi/temp/kodi.log
# To see print statements in the log, press Ctrl-Shift-D on Kodi machine

# This is an object that represents a device on which the Tasmota firmware is running

import requests
import service # service.py
import json 

class TasmotaDevice():

    def __init__(self,  address,  port):
        self.address = address
        self.port = str(port)
        self.get_properties_from_device()
        self.nicename = "http://"+ self.address + ":" + self.port
        self.get_properties_from_device()

    def get_properties_from_device(self):
        params = (
            ('cmnd', 'Status 0'),
        )
        response = requests.get("http://"+ self.address + ":" + self.port +"/cm", headers=service.headers, params=params)
        
        j = json.loads(response.text)
        print(j["Status"]["FriendlyName"][0])
        self.nicename = j["Status"]["FriendlyName"][0]
        print(json.dumps(j, indent=2, sort_keys=True)) # Print the complete self-description JSON we got from the device

    def __repr__(self):
         return "%s at %s:%s" % (self.nicename, self.address, self.port)
         
# TODO: Make it possible to set the color, brightness, etc.
