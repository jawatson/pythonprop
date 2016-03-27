include $(top_srcdir)/gnome-doc-utils.make
dist-hook: doc-dist-hook

DOC_MODULE = voacapgui
DOC_ENTITIES = legal.xml

DOC_FIGURES = figures/antenna_chooser.png \
	figures/main_window.png \
	figures/site_chooser.png \
	figures/area_plot_configure.png \
	figures/p2p_plot_configure.png \
	figures/ssn_tab.png \
	figures/area_tab.png \
	figures/p2p_tab.png \
	figures/system_tab.png


pdfdir = $(pkgdatadir)/docs

pdf_DATA = voacapgui.pdf voacapgui-C.omf

EXTRA_DIST = $(pdf_DATA) 

voacapgui.pdf: C/voacapgui.xml C/legal.xml
	dblatex C/voacapgui.xml -o voacapgui.pdf

DISTCLEANFILES = $(pdf_DATA)

