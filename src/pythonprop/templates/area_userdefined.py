


import sys, os, re

class templates:
    ''' This class returns a set of templates to the caller.
    This class serves the purpose of letting the no-code user write simple
    area templates in a text file.
    #--------------------------------------------------
    #
    #    format for area plot user defined templates:
    #    lines starting with # are ignored
    #    each line consist in three values separated by spaces
    #    each template is enclosed between "<template name>"
    #    and "</template>" tags.
    #
    #    month utchour freq
    #    11    22      14.250
    #    month: number month, 1=January
    #    utchour: UTC time HOUR, 00 to 23
    #    freq: frequecy in MHz
    #
    #   # example: all months at midnight on 14.100 MHz
    #   <template All months midnight 14.100 Mhz>
    #   #year month utchour freq
    #   2010      01      00      14.10
    #   2010      02      00      14.10
    #   2010      03      00      14.10
    #   2010      04      00      14.10
    #   2010      05      00      14.10
    #   2010      06      00      14.10
    #   2010      07      00      14.10
    #   2010      08      00      14.10
    #   2010      09      00      14.10
    #   2010      10      00      14.10
    #   2010      11      00      14.10
    #   2010      12      00      14.10
    #   </template>
    #
    #--------------------------------------------------
    '''

    name = 'User Defined Templates'
    description = 'Set of templates defined by the user'

    def __init__(self, parent, ssn_repo):
        self.parent = parent
        self.ssn_repo = ssn_repo
        self.ret_templates = {} # { templatename : [(month_i,utc,freq),...]}
        self.area_templates_file = None


    def get_names(self):
        return list(self.ret_templates.keys())

    def get_params(self):
        return ['area_templates_file',]

    def load(self):
        if not self.area_templates_file: return -1
        re_tag_name = re.compile(r'\[(.*)\]')
        fd = None
        try:
            fd = open(os.path.expandvars(self.area_templates_file))
        except Exception as X:
            print(_("Can't open template file <%(f)s> -> <%(p)s>.") % {'tf':self.area_templates_file,
                        'p':os.path.expandvars(self.area_templates_file)})
            return -1
        if fd:
            lines = fd.readlines()
            fd.close()
            templ_n = None
            for line in lines:
                line.strip()
                if line[0] == '#': continue
                if line[0] == '\n': continue
                if not len(line): continue
                if line.isspace(): continue
                # this is the template name tag, until next tag or EOF
                # all significative lines are part of this template
                m = re_tag_name.match(line)
                if m:
                    templ_n = m.groups()[0].strip()
                    self.ret_templates[templ_n] = []
                    continue
                # append line
                y,m,u,f = line.split()
                try:
                    tup = (int(y),int(m),int(u),float(f))
                except Exception as X:
                    print(_("Can't convert values: <%s>") % line)
                    # could be better to remove the entire template here...
                    continue
                if templ_n:
                    self.ret_templates[templ_n].append(tup)
            return


    def set_ini(self, model):
        return
    def run(self):
        return

    def area_save_as_template(self, *args):
        ''' saves area_tv model content as a template '''
        global ok_bt
        global nentry

        def text_change(self, *args):
            global ok_bt
            global nentry
            if len(nentry.get_text()):
                ok_bt.set_sensitive(True)
            else:
                ok_bt.set_sensitive(False)

        dialog = Gtk.Dialog(_("Creating new area template"),
                   self.parent,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT))
        hb = Gtk.HBox(2)
        label = Gtk.Label(label=_("Template name"))
        hb.pack_start(label, True, True, 0)
        nentry = Gtk.Entry(max=50)
        nentry.connect("changed", text_change)
        hb.pack_start(nentry, True, True, 0)
        hb.show_all()
        dialog.vbox.pack_start(hb, True, True, 0)

        ok_bt = Gtk.Button(None, Gtk.STOCK_OK)
        ok_bt.set_sensitive(False)
        ok_bt.show()
        dialog.add_action_widget(ok_bt, Gtk.ResponseType.ACCEPT)

        response = dialog.run()
        if response == -3: # accept
            # save it
            fd = open(os.path.expandvars(self.area_templates_file), 'a')
            fd.write(_('\n#template created by voacap GUI'))
            title = nentry.get_text()
            fd.write('\n[%s]' % title)
            fd.write(_('\n#month utchour  freq'))
            model = self.area_tv.get_model()
            iter = model.get_iter_first()
            while iter:
                m,u,f = model.get(iter,1,2,3)
                fd.write('\n%02d      %02d      %.3f' % (m,u,float(f)))
                iter = model.iter_next(iter)
            fd.write(_('\n#End of %s') % title)
            fd.close()
            # reload templates_file to repopulate templatescb, then
            # select this recently saved as the active one
            self.build_area_template_ts()
            model = self.templatescb.get_model()
            iter = model.get_iter_first()
            while iter:
                if model.get_value(iter, 0) == title:
                    self.templatescb.set_active_iter(iter)
                    break
                iter = model.iter_next(iter)
        dialog.destroy()




    def build_new_template_file(self):
        fn = os.path.join(self.prefs_dir,'area_templ.ex')
        s = _('''# rough format for area plot templates:
# lines starting with # are ignored
# each line consist in three values separated by spaces
# each template is preceded by a name enclosed in square brackets:
# [template name]
# tags
# month utchour freq
# 11    22      14.250
# month: number month, 1=January
# utchour: UTC time HOUR, 00 to 23
# freq: frequecy in MHz

# example: all months at midnight on 14.100 MHz
[All months midnight 14.100 Mhz]
#year month utchour freq
2010      01      00      14.10
2010      02      00      14.10
2010      03      00      14.10
2010      04      00      14.10
2010      05      00      14.10
2010      06      00      14.10
2010      07      00      14.10
2010      08      00      14.10
2010      09      00      14.10
2010      10      00      14.10
2010      11      00      14.10
2010      12      00      14.10

[All months at 1600z 7.500 MHz]
#month utchour freq
2010      01      16      7.5
2010      02      16      7.5
2010      03      16      7.5
2010      04      16      7.5
2010      05      16      7.5
2010      06      16      7.5
2010      07      16      7.5
2010      08      16      7.5
2010      09      16      7.5
2010      10      16      7.5
2010      11      16      7.5
2010      12      16      7.5
\n
''')
        with open(fn, 'w') as templates_def_fd:
            templates_def_fd.write(s)
        self.area_templates_file = fn
