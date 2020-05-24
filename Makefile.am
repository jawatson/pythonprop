## Process this file with automake to produce Makefile.in

## http://www.micahcarrick.com/tutorials/autotools-tutorial-python-gtk/getting-started.html#section_4

SUBDIRS = data src 

man_MANS = \
	man/voaAreaPlot.1 \
	man/voaP2PPlot.1

EXTRA_DIST=\
	$(man_MANS) \
	gnome-doc-utils.make \
	m4
	
DISTCLEANFILES = gnome-doc-utils.make
DISTCHECK_CONFIGURE_FLAGS = --disable-scrollkeeper
