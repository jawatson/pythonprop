AC_INIT(pythonprop, 0.24)

AM_INIT_AUTOMAKE
AM_PATH_PYTHON([3.4])

AC_ARG_WITH([online-help],
            [AS_HELP_STRING([--without-online-help],
              [disable support for online-help])],
            [],
            [with_online_help=yes])

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
