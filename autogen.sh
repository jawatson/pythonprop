#! /bin/sh

mkdir -p m4 \
  && aclocal -I m4 \
  && gnome-doc-prepare \
  && aclocal -I m4

aclocal \
  && automake --add-missing \
  && autoconf
