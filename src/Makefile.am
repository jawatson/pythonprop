## Process this file with automake to produce Makefile.in

## http://www.micahcarrick.com/tutorials/autotools-tutorial-python-gtk/getting-started.html#section_4

SUBDIRS = pythonprop

bin_SCRIPTS=\
	voa3DPlot \
	voaAreaPlot \
	voacapgui \
	voaAreaPlotgui \
	voaP2PPlot \
	voaP2PPlotgui \
	voaP2PPlotServer 

CLEANFILES = $(bin_SCRIPTS)

EXTRA_DIST=\
	voa3DPlot.in \
	voaAreaPlot.in \
	voacapgui.in \
	voaAreaPlotgui.in \
	voaP2PPlot.in \
	voaP2PPlotgui.in \
	voaP2PPlotServer.in 
#	$(nobase_pkgdata_SCRIPTS) \
#	$(nobase_pkgdata_DATA) \
#	$(man_MANS) \
#	$(bin_SCRIPTS)

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

voa3DPlot: voa3DPlot.in Makefile
	$(do_substitution) < $(srcdir)/voa3DPlot.in > voa3DPlot
	chmod +x voa3DPlot

voaAreaPlot: voaAreaPlot.in Makefile
	$(do_substitution) < $(srcdir)/voaAreaPlot.in > voaAreaPlot
	chmod +x voaAreaPlot

voacapgui: voacapgui.in Makefile
	$(do_substitution) < $(srcdir)/voacapgui.in > voacapgui
	chmod +x voacapgui

voaAreaPlotgui: voaAreaPlotgui.in Makefile
	$(do_substitution) < $(srcdir)/voaAreaPlotgui.in > voaAreaPlotgui
	chmod +x voaAreaPlotgui

voaP2PPlot: voaP2PPlot.in Makefile
	$(do_substitution) < $(srcdir)/voaP2PPlot.in > voaP2PPlot
	chmod +x voaP2PPlot

voaP2PPlotgui: voaP2PPlotgui.in Makefile
	$(do_substitution) < $(srcdir)/voaP2PPlotgui.in > voaP2PPlotgui
	chmod +x voaP2PPlotgui

voaP2PPlotServer: voaP2PPlotServer.in Makefile
	$(do_substitution) < $(srcdir)/voaP2PPlotServer.in > voaP2PPlotServer
	chmod +x voaP2PPlotServer




