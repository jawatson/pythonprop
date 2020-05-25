#! /bin/sh

GNOMEDOC=`which yelp-build`
if test -z $GNOMEDOC; then
        echo "*** The tools to build the documentation are not found,"
        echo "    please install the yelp-tools package ***"
        exit 1
fi

mkdir -p m4 \
  && aclocal -I m4 

aclocal \
  && automake --add-missing \
  && autoconf
