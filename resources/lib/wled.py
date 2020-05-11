# To see the log:
#  cat ~/.kodi/temp/kodi.log
# To see print statements in the log, press Ctrl-Shift-D on Kodi machine

# This is an object that represents a device on which the WLED firmware is running

import requests
import service # service.py
import json 

class WledDevice():

    def __init__(self,  address,  port):
        self.address = address
        self.port = str(port)
        self.get_properties_from_device()
        self.nicename = "http://"+ self.address + ":" + self.port
        self.get_properties_from_device()

    def get_properties_from_device(self):
        response = requests.get("http://"+ self.address + ":" + self.port +"/json", headers=service.headers)
        j = json.loads(response.text)
        print(j["info"]["name"])
        self.nicename = j["info"]["name"]
        print(json.dumps(j, indent=2, sort_keys=True)) # Print the complete self-description JSON we got from the device
        
    def __repr__(self):
         return "%s at %s:%s" % (self.nicename, self.address, self.port)
         
# TODO: Make it possible to set the color, brightness, etc.
# To set a color, WLED wants R, G, B values
# R,  G,  B,  "0"
# data = '{"seg":{"col":[[0,255,200,"0"],[],[]]},"transition":7,"v":true}'
# data = '{"seg":{"col":[[255,200,0,"0"],[],[]]},"transition":7,"v":true}'
