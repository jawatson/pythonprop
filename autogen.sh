#! /bin/sh

gnome-doc-prepare

aclocal \
  && automake --add-missing \
  && autoconf 

