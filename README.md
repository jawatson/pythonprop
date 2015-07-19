# pythonprop
VOACAP Utilities

#PythonProp
Pythonprop is a collection of scripts to provide a wrapper to the VOACAP HF 
propagation prediction engine.

The current stable GTK2 release is version 0.13 which will be the last 
version to be released using the PyGTK bindings.  

From v0.16, the application uses the GTK3 compatible PyGobject library.

#Installation

##User Install
The inclusion of Gnome documentation from v0.16 onwards requires a few additional 
dependencies;
* rarian-compat
* gnome-doc-utils
* pkg-config

The application itself requires a few python dependancies;
* matplotlib
* basemap

These can be installed on Fedora 22 with the 
following command;

    $ sudo yum install rarian-compat gnome-doc-utils pkgconfig python-basemap

Debian / Ubuntu users can install these dependancies with the following command;

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

##Running the Applictation
The application may be started by typing 'voacapgui' at the command line. v0.16
includes a .desktop file allowing the applictaion to be started from the system
application launcher.
