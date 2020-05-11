# Browse Zeroconf add-on

Browse services announced on the local network with Zeroconf (also known as Avahi, Bonjour, DNS-SD, Rendezvous)

## Installation

While you could install the plugin through the KODI graphical user interface, it may be quicker to ssh into the box and do:

```
cd /storage/.kodi/addons/
wget -c https://github.com/probonopd/sftp://root@alexelec.local/storage/.kodi/addons/plugin.program.zeroconfbrowse/archive/master.zip -O plugin.program.zeroconfbrowse.zip
unzip plugin.program.zeroconfbrowse.zip
mv plugin.program.zeroconfbrowse-master plugin.program.zeroconfbrowse
killall kodi.bin
```

## TODO

Pull requests are welcome. This is really easy Python code, after all.

* Implement continuous updating of the list of services in the GUI without blocking the GUI
* Handle known services

## References

* https://kodi.wiki/view/Add-on_development