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


if HAVE_DBLATEX
MANPDF = $(DOC_MODULE).pdf
doc_DATA = $(MANPDF)
EXTRA_DIST = $(MANPDF) 

$(MANPDF): C/voacapgui.xml 
	$(DBLATEX) C/voacapgui.xml -o voacapgui.pdf

CLEANFILES = $(MANPDF)
endif
