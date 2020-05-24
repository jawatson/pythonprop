AC_INIT(pythonprop, 0.30b3)

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([3.4])

# Check for presence of dblatex
AC_CHECK_PROG(DBLATEX, dblatex, dblatex)
if test -z "$DBLATEX"; then
  AC_MSG_WARN([dblatex not found, skipping build pdf docs.])
fi

AM_CONDITIONAL([HAVE_DBLATEX], [test -n "$DBLATEX"])

AC_ARG_WITH([online-help],
            [AS_HELP_STRING([--without-online-help],
              [disable support for online-help])],
            [],
            [with_online_help=yes])

AC_CONFIG_MACRO_DIR([m4])
GNOME_DOC_INIT

AC_CONFIG_FILES([
	Makefile
	data/Makefile
	data/voacapgui.desktop
	docs/user/help/Makefile
	src/Makefile
	src/pythonprop/Makefile
	src/pythonprop/templates/Makefile
	src/pythonprop/ui/Makefile
])
AC_OUTPUT
