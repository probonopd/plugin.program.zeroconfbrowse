# To see the log:
#  cat ~/.kodi/temp/kodi.log
# To see print statements in the log, press Ctrl-Shift-D on Kodi machine

# This is the GUI part of this addon; it relies on the non-GUI part to browse Zeroconf services

import sys
import xbmcgui
import xbmcplugin
import service as servicepy
from service import ZeroconfService # pickle.load needs this or else it gives: AttributeError: 'module' object has no attribute 'ZeroconfService'
import cPickle as pickle

def main():
    addon_handle = int(sys.argv[1])
    xbmcplugin.setContent(addon_handle, 'files') # There is no "generic" one?
    print("len of servicepy.services.services: %i" % len(servicepy.services.services)) # Seems always to be 0, why?
    # for service in servicepy.services.services: # Seems always to be 0, why?
    infile = open(servicepy.pickle_file,'rb')
    services = pickle.load(infile)
    print(services)
    infile.close()
    for service in services:
        li = xbmcgui.ListItem(str(service))
        li.setInfo('files', {'plot': service.address})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
    # FIXME: Ideally we want to refresh the screen only if a new service has been found or an existing one is gone
    # but for this we would probably need to get the global variable to work and get rid of pickle

if __name__ == "__main__":
    main()
