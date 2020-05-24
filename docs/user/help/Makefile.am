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

DOC_LINGUAS = en

MANPDF = $(DOC_MODULE).pdf
dist_doc_DATA = $(MANPDF) voacapgui-C.omf voacapgui-en.omf

if HAVE_DBLATEX

$(MANPDF): C/voacapgui.xml
	$(DBLATEX) C/voacapgui.xml -o voacapgui.pdf

CLEANFILES = $(MANPDF)

endif
