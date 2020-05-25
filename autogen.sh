#! /bin/sh

mkdir -p m4 \
  && aclocal -I m4 \
  && yelp-build \
  && aclocal -I m4

aclocal \
  && automake --add-missing \
  && autoconf
