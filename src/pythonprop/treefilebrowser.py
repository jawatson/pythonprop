# -*- coding: utf-8 -*-

"""
TreeFileBrowser a tree-like gtk file browser
Copyright (C) 2006-2007 Adolfo González Blázquez <code@infinicode.org>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version. 

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

If you find any bugs or have any suggestions email: code@infinicode.org
"""

# Modified by J. Watson to accept the view as an init argument

# Replaced the soon to be deprecated 'dircache' with 'os'

# Further modified by J.Watson to implement a directory filter.
# Only directories with the specified file type somewhere under them 
# will be displayed.

try:
    from gi.repository import Gtk
    from gi.repository import GObject
    from gi.repository import GdkPixbuf
except:
    raise SystemExit
    
import gi
""" todo pygobject
if Gtk.pygtk_version < (2, 0):
      print _("PyGtk 2.0 or later required for this widget")
      raise SystemExit
"""  
try:
    from os import path as ospath
    import os
    from . import scriptutil
    #import dircache
except:
    raise SystemExit

class TreeFileBrowser():
    """ A widget that implements a tree-like file browser, like the
    one used on Nautilus spatial view in list mode """
    
    __gproperties__ = {
        'show-hidden': (GObject.TYPE_BOOLEAN, 'show hidden files', 
                        'show hidden files and folders', False, GObject.PARAM_READWRITE),
        'show-only-dirs': (GObject.TYPE_BOOLEAN, 'show only directories',
                           'show only directories, not files', True, GObject.PARAM_READWRITE),
        'rules-hint': (GObject.TYPE_BOOLEAN, 'rules hint',
                       'show rows background in alternate colors', True, GObject.PARAM_READWRITE),
        'root': (GObject.TYPE_STRING, 'initial path',
                 'initial path selected on tree browser', '/', GObject.PARAM_READWRITE)
    }
    
    #__gsignals__ = { 'row-expanded' : (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_STRING,)),
    #                 'cursor-changed' : (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_STRING,))
    #}
    
    def __init__(self, root=None, view=None, file_types=None):
        """ Path is where we want the tree initialized """
        
        #GObject.GObject.__init__(self)
        self.file_types = file_types
        
        self.show_hidden = False
        self.show_only_dirs = False
        self.show_rules_hint = True
        
        self.root = '/'
        if root != None and ospath.isdir(root): self.root = root
        #else: print "%s doesn't exist. Setting root to default %s" % (root, self.root)
        
        self.view = self.make_view(view = view)
        self.create_new()
        self.view.expand_all()
        
    #####################################################
    # Accessors and Mutators
    
    def do_get_property(self, property):
        """ GObject get_property method """
        if property.name == 'show-hidden':
            return self.show_hidden
        elif property.name == 'show-only-dirs':
            return self.show_only_dirs
        elif property.name == 'rules-hint':
            return self.show_rules_hint
        elif property.name == 'path':
            return self.root
        else:
            raise AttributeError(_('unknown property %s') % property.name)
    
    def do_set_property(self, property, value):
        """ GObject set_property method """
        if property.name == 'show-hidden':
            self.show_hidden = value
        elif property.name == 'show-only-dirs':
            self.show_only_dirs = value
        elif property.name == 'rules-hint':
            self.show_rules_hint = value
        elif property.name == 'path':
            self.root = value
        else:
            raise AttributeError(_('unknown property %s') % property.name)
    
    def get_view(self):
        return self.view
    
    def set_show_hidden(self, hidden): 
        self.show_hidden = hidden
        self.create_new()
        
    def get_show_hidden(self):
        return self.show_hidden
        
    def set_rules_hint(self, rules):
        self.show_rules_hint = rules
        self.view.set_rules_hint(rules)
        
    def get_rules_hint(self):
        return self.show_rules_hint
    
    def set_show_only_dirs(self, only_dirs):
        self.show_only_dirs = only_dirs
        self.create_new()
        
    def get_show_only_dirs(self):
        return self.show_only_dirs
    
    def get_selected(self):
        """ Returns selected item in browser """
        model, iter = self.view.get_selection().get_selected()
        if iter != None:
            return model.get_value(iter, 2)
        else:
            return None


    #####################################################
    # Callbacks

    def row_expanded(self, treeview, iter, path):
        """ CALLBACK: a row is expanded """
        
        model = treeview.get_model()
        model.set_value(iter, 0, self.get_folder_opened_icon())
        self.get_file_list(model, iter, model.get_value(iter,2))
        self.remove_empty_child(model, iter)
        
        # Send signal with path of expanded row
        #self.emit('row-expanded', model.get_value(iter,2))


    def row_collapsed(self, treeview, iter, path):
        """ CALLBACK: a row is collapsed """
        
        model = treeview.get_model()
        model.set_value(iter, 0, self.get_folder_closed_icon())
        while model.iter_has_child(iter):
            child = model.iter_children(iter)
            model.remove(child)
        self.add_empty_child(model, iter)
    

    def row_activated(self, treeview, path, view_column):
        """ CALLBACK: row activated using return, double-click, shift-right, etc. """
        
        if treeview.row_expanded(path):
            treeview.collapse_row(path)
        else:
            treeview.expand_row(path, False)
    
    
    def cursor_changed(self, treeview):
        """ CALLBACK: a new row has been selected """
        model, iter = treeview.get_selection().get_selected()
        # Send signal with path of expanded row
        # self.emit('cursor-changed', model.get_value(iter,2))


    #####################################################
    # Directories and files, nodes and icons
    
    def set_cursor_on_first_row(self):
        model = self.view.get_model()
        iter = model.get_iter_root()
        path = model.get_path(iter)
        self.view.set_cursor(path)
    
    def set_active_dir(self, directory):

        rootdir = self.root

        # Expand root
        model = self.view.get_model()
        iter = model.get_iter_root()
        path = model.get_path(iter)
        self.view.expand_row(path, False)
        iter = model.iter_children(iter)

        # Add trailing / to paths
        if len(directory) > 1 and directory[-1] != '/': directory += '/'
        if len(rootdir) > 1 and rootdir[-1] != '/':  rootdir += '/'

        if not ospath.isdir(directory) or not (rootdir in directory) or (directory == rootdir):
            return False
        else:
            
            # Now we check if the desired dir is valid
            # Convert the given '/home/user/dir/' to ['/', 'home/', 'user/', 'dir/']
            if len(directory) > 1: 
                dirtree = directory.split('/')
                dirtree.pop(-1)
            else: dirtree = ['/']
            if len(dirtree) > 1: 
                dirtree[0] = '/'
                for i in range(len(dirtree)-1): dirtree[i+1] = dirtree[i+1] + '/'
            
            # Convert root to '/home/user/dir/' to ['/', 'home/', 'user/', 'dir/']
            if len(rootdir) > 1: 
                roottree = rootdir.split('/')
                roottree.pop(-1)
            else: roottree = ['/']
            if len(roottree) > 1:
                roottree[0] = '/'
                for i in range(len(roottree)-1): roottree[i+1] = roottree[i+1] + '/'
            
            # Check if the dir is in the same path as the desired root
            long = len(roottree)
            for i in range(int):
                if  roottree[i] != dirtree[i]: return False
            
            # End checking
            
            # Star expanding
            # Count how many iterations we need
            depth = len(dirtree) - len(roottree)
            
            # Expand depends on the rootdir. Ugly ugly hack!
            if rootdir == '/': exp = 1
            else: exp = 2
            
            # Expand baby expand!
            for i in range(depth):
                newpath = dirtree[i+exp]
                val = model.get_value(iter, 1).replace('/','') + '/'
                while val != newpath:
                    iter = model.iter_next(iter)
                    val = model.get_value(iter, 1).replace('/','') + '/'
                
                path = model.get_path(iter)
                self.view.expand_row(path, False)
                iter = model.iter_children(iter)
            
            # Set the cursor
            self.view.set_cursor(path)
            
            return True
    
    
    def add_empty_child(self, model, iter):
        """ Adds a empty child to a node.
        Used when we need a folder that have children to show the expander arrow """
        
        model.insert_before(iter, None)


    def remove_empty_child(self, model, iter):
        """ Delete empty child from a node.
        Used to remove the extra child used to show the expander arrow
        on folders with children """
        
        newiter = model.iter_children(iter)
        model.remove(newiter)
        
        
    def get_file_list(self, model, iter, dir):
        """ Get the file list from a given directory """
        
        ls = os.listdir(dir)
        ls.sort(key=str.lower)
        for i in ls:
            path = ospath.join(dir,i)
            if ospath.isdir(path) or not self.show_only_dirs :
                if (ospath.isdir(path) and len(scriptutil.ffind(path, shellglobs=self.file_types))>0) or not ospath.isdir(path):
                    if i[0] != '.' or (self.show_hidden and i[0] == '.'):
                        newiter = model.append(iter)
                        if ospath.isdir(path): icon = self.get_folder_closed_icon()
                        else: icon = self.get_file_icon()
                        model.set_value(newiter, 0, icon)    
                        model.set_value(newiter, 1, i)
                        model.set_value(newiter, 2, path)
                        if ospath.isdir(path):
                            try: subdir = os.listdir(path)
                            except: subdir = []
                            if subdir != []:
                                for i in subdir:
                                    if ospath.isdir(ospath.join(path,i)) or not self.show_only_dirs:
                                        if i[0] != '.' or (self.show_hidden and i[0] == '.'):
                                            self.add_empty_child(model, newiter)
                                            break


    def create_root(self):
        model = self.view.get_model()

        if self.root != '/': directory = self.root.split('/')[-1]
        else: directory = self.root

        iter = model.insert_before(None, None)
        model.set_value(iter, 0, self.get_folder_opened_icon())    
        model.set_value(iter, 1, directory)
        model.set_value(iter, 2, self.root)
        iter = model.insert_before(iter, None)
        return iter

    def create_new(self):
        """ Create tree from scratch """
        
        model = self.view.get_model()
        model.clear()
        iter = self.create_root()
        self.get_file_list(self.view.get_model(), iter, self.root)

    def get_folder_closed_icon(self):
        """ Returns a pixbuf with the current theme closed folder icon """
        
        icon_theme = Gtk.IconTheme.get_default()
        try:
            icon = icon_theme.load_icon("gnome-fs-directory", Gtk.IconSize.MENU, 0)
            return icon
        except GObject.GError as exc:
            print(_("Can't load icon"), exc)
            return None
    
    
    def get_folder_opened_icon(self):
        """ Returns a pixbuf with the current theme opened folder icon """
        
        icon_theme = Gtk.IconTheme.get_default()
        try:
            icon = icon_theme.load_icon("gnome-fs-directory-accept", Gtk.IconSize.MENU, 0)
            return icon
        except GObject.GError as exc:
            print(_("Can't load icon"), exc)
            return None
        
        
    def get_file_icon(self):
        """ Returns a pixbuf with the current theme file icon """
        
        icon_theme = Gtk.IconTheme.get_default()
        try:
            icon = icon_theme.load_icon("text-x-generic", Gtk.IconSize.MENU, 0)
            return icon
        except GObject.GError as exc:
            print(_("Can't load icon"), exc)
            return None


    #####################################################
    # Model

    def make_view(self, view = None):
        """ Create the view itself.
            (Icon, dir name, path) """
        model = Gtk.TreeStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING, GObject.TYPE_STRING)
        
        view.set_model(model)
        view.set_headers_visible(False)
        view.set_enable_search(True)
        view.set_reorderable(False)
        view.set_rules_hint(self.show_rules_hint)
        view.connect('row-expanded',  self.row_expanded)
        view.connect('row-collapsed', self.row_collapsed)
        view.connect('row-activated', self.row_activated)
        view.connect('cursor-changed', self.cursor_changed)
        
        col = Gtk.TreeViewColumn()
        
        # The icon
        render_pixbuf = Gtk.CellRendererPixbuf()
        col.pack_start(render_pixbuf,False)
        col.add_attribute(render_pixbuf, 'pixbuf', 0)
        
        # The dir name
        render_text = Gtk.CellRendererText()
        col.pack_start(render_text, False)
        col.add_attribute(render_text, 'text', 1)
        
        view.append_column(col)
        view.show()
    
        return view


# End TreeFileBrowser
