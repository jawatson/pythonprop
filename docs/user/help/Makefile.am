@YELP_HELP_RULES@

HELP_ID = voacapgui
HELP_FILES = index.docbook \
	legal.xml

HELP_MEDIA = figures/antenna_chooser.png \
	figures/main_window.png \
	figures/site_chooser.png \
	figures/area_plot_configure.png \
	figures/p2p_plot_configure.png \
	figures/ssn_tab.png \
	figures/area_tab.png \
	figures/p2p_tab.png \
	figures/system_tab.png

HELP_LINGUAS = 

MANPDF = $(HELP_ID).pdf

dist_doc_DATA = $(MANPDF)

if HAVE_DBLATEX

.PHONY: $(MANPDF)
	
$(MANPDF): C/index.docbook
	$(DBLATEX) C/index.docbook -o voacapgui.pdf

endif
