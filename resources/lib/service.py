# To see the log:
#  cat ~/.kodi/temp/kodi.log
# To see print statements in the log, press Ctrl-Shift-D on Kodi machine

# This is the non-GUI part of this addon; it provides the GUI part with the Zeroconf services found on the network

import sh # http://amoffat.github.io/sh - a single python file - wget https://raw.githubusercontent.com/amoffat/sh/develop/sh.py
import requests # Not there on LibreELEC by default
import threading
import cPickle as pickle
import xbmc

import wled # wled.py

global services # FIXME: This means that we will be able to use services from other python files - at least in theory but it doesn't seem to work. Why?

global pickle_file 
pickle_file = '/run/zeroconf.services.pickle'

headers = {
    'User-Agent': 'python-requests/0.0',
    'Accept': '*/*',
    'Content-type': 'application/json; charset=UTF-8',
    'Connection': 'keep-alive',
}

global target_brightness
global target_color
target_brightness = "255" # Max

class ZeroconfService():

    def __init__(self, avahi_browse_line):
        parts = avahi_browse_line.split(";")
        self.interface =parts[1]
        self.ip_version = parts[2]
        self.name = parts[3]
        self.service_type = parts[4]
        self.domain = parts[5]
        self.hostname_with_domain = parts[6]
        self.address = parts[7]
        self.port = parts[8]
        self.txt = parts[9]

    def __repr__(self):
        return "%s on %s:%s" % (self.service_type, self.hostname_with_domain, self.port)
    
    # Define here what we should do with detected services. This gets run whenever a service is added
    def handle(self):
        # ESP8266 devices running the WLED sketch - we can e.g., set the color
        if self.service_type == "_wled._tcp":
            try:
                data = '{"seg":{"col":[[0,0,'+target_brightness+' ,"0"],[],[]]},"transition":7,"v":true}'
                response = requests.post("http://"+self.address+":"+self.port+"/json/state", headers=headers, data=data)
                print(response)
            except:
                pass
        # Devices running an MQTT broker - we can e.g., send them some MQTT messages
        # TODO: Implement this, or hook into an existing add-on that already does this
        #
        # ESP8266 devices running the Tasmota sketch - we can e.g., switch power sockets on/off or change lights
        if "tasmota" in self.name or "teckin" in self.name:
            try:
                params = (
                    ('m', '1'), # Amount of warm white
                    ('h0', '256'), # Color red 1-359 red (256=blue)
                    ('d0', remap(int(target_brightness), 0, 255, 0, 100)), # Brightness 0-100
                    ('n0',  '100'), # white only 0-100 full color
                )
                response = requests.get("http://"+self.address+":"+self.port, headers=headers, params=params)
                print(response.text)
            except:
                pass
        
class ZeroconfServices():

    def __init__(self):
        self.services = []

    def add(self, service):
        print("Appending " + str(service))
        self.services.append(service)
        # self.services.sort()
        self.save()
        service.handle()
                
    def remove(self, avahi_browse_line):
        print("TODO: To be implemented: Remove the service from the list if certain criteria match")
        self.save()
        # for service in self.services:
            # print(service.service_type)
            # print(service.hostname_with_domain)
            
    def save(self):
        outfile = open(pickle_file,'wb')
        pickle.dump(self.services, outfile)
        outfile.close()

# into which we import this one, too; https://stackoverflow.com/a/60504223
services = ZeroconfServices()

def long_running_function():
    avahi_browse = sh.Command("avahi-browse")
    print("Keep browsing Zeroconf services with avahi-browse -rlp and do not return...")
    print("This will detect devices that are switched on after this service has been started")
    for line in avahi_browse("-arlp", _iter=True):
        print(line)
        if line.startswith("="):
            s = ZeroconfService(line)
            services.add(s)
        if line.startswith("-"):
            services.remove(line)

if __name__ == "__main__":

    t1 = threading.Thread(target=long_running_function)
    t1 .daemon = True # Needed for Ctrl-C to work properly
    t1.start()

    # We need to periodically check if Kodi is exiting.
    # The addon is responsible for terminating when Kodi wants to exit.
    # https://kodi.wiki/view/Service_add-ons
    monitor = xbmc.Monitor()    
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            # Abort was requested while waiting. We should exit
            break

    # Call a scenario when Kodi is shutting down
    target_color = 128 # TODO: Do a more useful scenario
    for service in services:
        service.handle()

# https://www.arduino.cc/en/reference/map
# https://stackoverflow.com/a/43567380
def remap(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
  
# TODO:
# Add some actions, e.g.,
# Scenarios - how can we make those SUPER simple to configure?
# E.g., Tagesschau = blue light

# TODO:
# Make all lights go dark and possibly shut some devices down when Kodi shuts down
