
desktopdir = $(datadir)/applications
icondir = $(datadir)/icons

desktop_DATA = voacapgui.desktop

dist_icon_DATA = pythonprop.png

UPDATE_DESKTOP = update-desktop-database $(datadir)/applications || :

install-data-hook: 
	$(UPDATE_DESKTOP)
uninstall-hook: 
	$(UPDATE_DESKTOP)
