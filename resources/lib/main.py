import sh # http://amoffat.github.io/sh - a single python file - wget https://raw.githubusercontent.com/amoffat/sh/develop/sh.py
import requests # Not there on LibreELEC by default
import threading
import sys
import xbmcgui
import xbmcplugin
import time

do_refreshes = False # While initially populating the list of devices, we don't want to refresh each time. Only after the initial list has quiesced

# We want to have an always up-to-date list of available services on the network.
# We keep this list in the services instance of the Services() class until
# someone implements a better solution e.g., using dbus

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
                set_wled_to_blue = '{"seg":{"col":[[0,0,255,"0"],[],[]]},"transition":7,"v":true}'
                response = requests.post("http://"+self.address+":"+self.port+"/json/state", headers=headers, data=set_wled_to_blue)
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
                    ('h0', '256'), # Color (256=blue)
                    ('d0', '100'), # Brightness
                    ('n0', '100'), # Color intensity
                )
                response = requests.get("http://"+self.address+":"+self.port, headers=headers, params=params)
                print(response)
            except:
                pass
        
class ZeroconfServices():

    def __init__(self):
        self.services = []

    def add(self, service):
        self.services.append(service)
        # self.services.sort()
        service.handle()
                
    def remove(self, avahi_browse_line):
        print("TODO: To be implemented: Remove the service from the list if certain criteria match")
        # for service in self.services:
            # print(service.service_type)
            # print(service.hostname_with_domain)

services = ZeroconfServices()

headers = {
    'User-Agent': 'python-requests/0.0',
    'Accept': '*/*',
    'Content-type': 'application/json; charset=UTF-8',
    'Connection': 'keep-alive',
}

set_wled_to_blue = '{"seg":{"col":[[0,0,255,"0"],[],[]]},"transition":7,"v":true}'

avahi_browse = sh.Command("avahi-browse")

print("Keep browsing _wled._tcp services with avahi-browse -rlp and do not return...")
print("This can be used to detect devices that are switched on after this service has been started")

# Refresh the list on screen
def list_refresh():
    for service in services.services:
        li = xbmcgui.ListItem(str(service))
        li.setInfo('files', {'plot': service.address})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    # xbmc.executebuiltin("Container.Refresh") # Without this a cached directory listing is shown; with this the spinner is shown all the time... why?
    # FIXME: Ideally we want to refresh the screen only if a new service has been found or an existing one is gone
    
# TODO: Turn this into a Kodi background service that other plugins can query, too
def long_running_function():
    for line in avahi_browse("-arlp", _iter=True):
        print(line)
        if line.startswith("="):
            s = ZeroconfService(line)
            services.add(s)
            
        if line.startswith("-"):
            services.remove(line)
        if(do_refreshes == True):
            list_refresh()

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'files') # There is no "generic" one?

t1 = threading.Thread(target=long_running_function)
t1.daemon = True # Needed for Ctrl-C to work properly
t1.start()

time.sleep(5) # We need to wait here for some time to get the initial list
list_refresh() # TODO: Make this auto-updating without blocking the screen with the spinner all the time as the above code would do
# xbmc.executebuiltin("Container.Refresh") # Without this a cached directory listing is shown
do_refreshes = True


# TODO:
# Turn this into an add-on that contains both a service (no GUI) and a plugin (GUI)
# https://kodi.wiki/view/Service_add-ons
# so that the service runs all the time and can handle Zeroconf devices also while
# the GUI is not open. This may also allow the GUI to significantly speed up because
# the scanning for devices does not need to be done once the user opens the GUI but
# already has been done in the background at that time. The challenge is to make the 
# data exhange between the two separate Python scripts happen, see
# https://forum.kodi.tv/showthread.php?tid=198862&pid=1743342#pid1743342

# TODO:
# Add some actions, e.g.,
# Scenarios - how can we make those SUPER simple to configure?
# E.g., Tagesschau = blue light

# TODO:
# Make all lights go dark and possibly shut some devices down when Kodi shuts down

# TODO:
# Get the real nice names for Tasmota/Sonoff devices from their self-description JSON
# http://192.168.0.28/cm?cmnd=Status+0
# has
# Status.FriendlyName.0
# and a LOT more information about Tasmota devices
# The question is whether we should put the Tasmota handling into its own add-on... at which point it becomes "work"...
