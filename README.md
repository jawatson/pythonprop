# pythonprop
VOACAP Utilities

#PythonProp
Pythonprop is a collection of scripts to provide a wrapper to the VOACAP HF
propagation prediction engine.

From v0.16, the application uses the GTK3 compatible PyGobject library.

#Installation (Python 3)
From version v.20, the application uses Python 3, supported on the current
version of most major distros.  New users are encouraged to use the Python 3
version of the application .

The application requires the following dependancies;
* python3-matplotlib
* python3-basemap
* python3-matplotlib-gtk3
* python3-cairocffi
* rarian-compat
* gnome-doc-utils
* pkg-config
* yelp


These can be installed on Fedora 23 with the following command;

    $ sudo dnf install yelp rarian-compat gnome-doc-utils \
      pkgconfig python3-dateutil python3-basemap \
      python3-cairocffi python3-cffi python3-matplotlib-gtk3

Debian / Ubuntu users can install these dependencies with the following command;

    $ sudo apt-get install yelp python3-gi python3-gi-cairo rarian-compat \
      gnome-doc-utils pkg-config python3-dateutil python3-mpltoolkits.basemap \
      python3-cairocffi python3-matplotlib-gtk3

The following commands will install the pythonProp tools from the .tar.gz file.

    $ ./configure
    $ sudo make install

Typing 'voacapgui' from the command line or the Gnome desktop will start the main application.


#Installation (Python 2)
New users are encouraged to use Python 3 (see above).  No further Python 2 updates are planned.

##User Install
The inclusion of Gnome documentation from v0.16 onwards requires a few additional
dependencies;
* rarian-compat
* gnome-doc-utils
* pkg-config

The application itself requires a few python dependancies;
* matplotlib
* basemap
* python-matplotlib-gtk3

These can be installed on Fedora 23 with the following command;

    $ sudo dnf install rarian-compat gnome-doc-utils pkgconfig python-basemap python-matplotlib-gtk3

Debian / Ubuntu users can install these dependencies with the following command;

    $ sudo apt-get install rarian-compat gnome-doc-utils pkg-config python-mpltoolkits.basemap

The following commands will install the pythonProp tools from the .tar.gz file.

    $ ./configure
    $ make
    $ sudo make install

Typing 'voacapgui' from the command line or the Gnome desktop will start the main application.

##Documentation
The tarball contains a pdf copy of the documentation which is copied this to the /usr/local/share/pythonprop/docs folder (default) by the 'make install' operation.  The same documentation is available via the Gnome help menu in the main application.

The command 'make pdf' will rebuild the pdf if required.  This command requires the use of dblatex.

##Developer Install
The following command will create the build structure from a fresh svn checkout;

    $ ./autogen.sh

##Running the Application
The application may be started by typing 'voacapgui' at the command line. v0.16
includes a .desktop file allowing the application to be started from the system
application launcher.

#Roadmap

##Release 0.22
* Add print buttons to the result views. Done 18/2
* Add the ability to save area plots in a zip ('.vgz') file containing, the
  input/output files and a meta.txt of notes / annotations and a file list.
* Add a load / save menu to load up a file and jump straight to the
  plotting function.  This same function could also restore the settings
  to permit the plot to be modified and recalculated.
* Add a few plot details to the voaAreaPlotgui combo (same as the P2P)

##Release 0.23
* Migrate mapping to cartopy

##Release 0.24
* Investigate running voacapl in a separate thread to provide some form of visual progress indicator.
