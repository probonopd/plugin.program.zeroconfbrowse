# To see the log:
#  cat ~/.kodi/temp/kodi.log
# To see print statements in the log, press Ctrl-Shift-D on Kodi machine

# This is the GUI part of this addon; it relies on the non-GUI part to browse Zeroconf services

import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import service as servicepy
from service import ZeroconfService # pickle.load needs this or else it gives: AttributeError: 'module' object has no attribute 'ZeroconfService'
import cPickle as pickle
import xbmc
import xbmcaddon

import tasmota # tasmota.py
import wled # wled.py

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'files') # There is no "generic" one?

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

# Initial menu that is shown when the add-on is opened
if mode is None:
    url = build_url({'mode': 'services'})
    li = xbmcgui.ListItem('Services announced by Zeroconf on the network')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)  
    url = build_url({'mode': 'scenarios'})
    li = xbmcgui.ListItem('Set scenarios')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

# Menu that is shown when "Services" is selected from the menu
elif mode[0] == 'services':
    print("len of servicepy.services.services: %i" % len(servicepy.services.services)) # Seems always to be 0, why?
    # for service in servicepy.services.services: # Seems always to be 0, why?
    infile = open(servicepy.pickle_file,'rb')
    services = pickle.load(infile)
    print(services)
    infile.close()
    for service in services:
        label = str(service)
        # For services that we know about and can handle, we show the nicename
        # which we get from the device (but not via Zeroconf)
        if "tasmota" in service.name or "teckin" in service.name:
            t = tasmota.TasmotaDevice(str(service.address),  str(service.port))
            label = t.nicename + " = " +  str(service)
        if "_wled" in service.service_type:
            w = wled.WledDevice(str(service.address),  str(service.port))
            label = w.nicename + " = " +  str(service)
        li = xbmcgui.ListItem(label)
        # li.setInfo('files', {'plot': label})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    # FIXME: Ideally we want to refresh the screen only if a new service has been found or an existing one is gone
    # but for this we would probably need to get the global variable to work and get rid of pickle

# Menu that is shown when "Scenarios" is selected from the menu
elif mode[0] == 'scenarios':
    url = build_url({'mode': 'scenario', 'brightness': '255'})
    li = xbmcgui.ListItem('Lights on')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    url = build_url({'mode': 'scenario', 'brightness': '128'})
    li = xbmcgui.ListItem('Lights dim')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    url = build_url({'mode': 'scenario', 'brightness': '64'})
    li = xbmcgui.ListItem('Lights off')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_handle)
    
# Action that thappens when a scenario is selected from the menu
elif mode[0] == 'scenario':
    brightness = args.get('brightness', None) 
    milliseconds = 3000
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(xbmcaddon.Addon().getAddonInfo('name'),'Brightness '+brightness[0], milliseconds,xbmcaddon.Addon().getAddonInfo('icon')))
    # TODO: Actually do something with it. E.g., let the service.py script know that a scenario was selected, and which one
    # (or call a function in service.py directly)?

    infile = open(servicepy.pickle_file,'rb')
    services = pickle.load(infile)
    for s in services:
        servicepy.target_brightness =  brightness[0]
        s.handle()
