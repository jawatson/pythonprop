
from gi.repository import Gtk
from datetime import datetime
from dateutil.relativedelta import relativedelta


class templates:
    name = 'Next N Months'

    def __init__(self, parent):
        self.parent = parent
        self.ret_templates = {} # { templatename : [(month_i,utc,freq),...]}
        self.current_month = None
        self.current_year = None
        self.current_utc = 12
        self.current_freq = 3.0
        self.iter = None

    def get_names(self):
        return [self.name,]

    def get_params(self):
        return []

    def load(self):
        return

    def set_ini(self, model):
        if len(model):
            iter = model.get_iter(len(model)-1)
            y,m,u,f = model.get(iter,0,2,3,4)
            self.current_year = y
            self.current_month = m
            self.current_utc = u if u else 12
            self.current_freq = float(f) if float(f) > 3 else 3.0


    def run(self):
        tups = []
        if not self.current_year:
            cur = datetime.now()
        else:
            cur = datetime(self.current_year, self.current_month, 1)
        if not self.current_month or not self.iter:
            dialog = Gtk.Dialog(_("Next N Months Area Template Properties"),
                       self.parent,
                       Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.WindowPosition.CENTER_ON_PARENT,
                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
            dialog.set_border_width(6)
            vb = Gtk.VBox()
            hb = Gtk.HBox(2)
            l = Gtk.Label(label=_('Number of months to add:'))
            l.set_alignment(0, 0.5)
            adj = Gtk.Adjustment(float(self.iter) if self.iter else 12, 1, 100, 1, 5, 0)
            em = Gtk.SpinButton()
            em.set_adjustment(adj)
            em.set_wrap(True)
            em.set_numeric(True)
            hb.pack_start(l, True, True, 0)
            hb.pack_end(em, True, True, 0)
            vb.pack_start(hb, True, True, 0)
            hb = Gtk.HBox(2)
            l = Gtk.Label(label=_('UTC hour:'))
            l.set_alignment(0, 0.5)
            adj = Gtk.Adjustment(self.current_utc, 1.0, 23.0, 1.0, 5.0, 0)
            eh = Gtk.SpinButton()
            eh.set_adjustment(adj)
            eh.set_wrap(True)
            eh.set_numeric(True)
            hb.pack_start(l, True, True, 0)
            hb.pack_end(eh, True, True, 0)
            vb.pack_start(hb, True, True, 0)
            hb = Gtk.HBox(2)
            adj = Gtk.Adjustment(self.current_freq, 3.0, 30.0, 0.1, 1.0, 0)
            l = Gtk.Label(label=_('Frequency (MHz):'))
            l.set_alignment(0, 0.5)
            ef = Gtk.SpinButton() #1.0, 3
            ef.set_adjustment(adj)
            ef.set_digits(3)
            ef.set_wrap(True)
            ef.set_numeric(True)
            hb.pack_start(l, True, True, 0)
            hb.pack_end(ef, True, True, 0)
            vb.pack_start(hb, True, True, 0)
            dialog.vbox.pack_start(vb, True, True, 0)
            dialog.show_all()

            ret = dialog.run()
            iter = em.get_value_as_int()
            utc = eh.get_value_as_int()
            freq = ef.get_value()
            dialog.destroy()
            if ret != -3: return 1

        else:
            utc = self.current_utc
            freq = self.current_freq
            iter = self.iter

        delta = relativedelta(months=+1)
        for i in range(iter):
            cur = cur + delta
            tups.append((cur.year, cur.month, utc, freq))
        self.ret_templates[self.name] = tups
