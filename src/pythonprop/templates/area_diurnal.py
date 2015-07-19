
from gi.repository import Gtk
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

# Template to run an area prediction at predefined hourly interval through a single day

class templates:
    name = 'Diurnal'

    def __init__(self, parent):
        self.parent = parent
        self.ret_templates = {} # { templatename : [(month_i,utc,freq),...]}

    def get_names(self):
        return [self.name,]

    def get_params(self):
        return []

    def load(self):
        return

    def set_ini(self, model):
        pass


    def run(self):
        tups = []
        current_time = datetime.now()
        
        dialog = Gtk.Dialog(_("Diurnal"),
                   self.parent,
                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.WindowPosition.CENTER_ON_PARENT,
                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dialog.set_border_width(6)
        vb = Gtk.VBox()
        
        hb = Gtk.HBox(2)
        label = Gtk.Label(label=_('Interval (hours):'))
        label.set_alignment(0, 0.5)
        intervals_store = Gtk.ListStore(str)
        intervals = ["1", "2", "3", "4", "6", "12"]
        for interval in intervals:
            intervals_store.append([interval])
        interval_combo = Gtk.ComboBox.new_with_model(intervals_store)
        renderer_text = Gtk.CellRendererText()
        interval_combo.pack_start(renderer_text, True)
        interval_combo.add_attribute(renderer_text, "text", 0)
        interval_combo.set_active(0)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(interval_combo, True, True, 0)
        vb.pack_start(hb, True, True, 0)
        
        hb = Gtk.HBox(2)
        label = Gtk.Label(label=_('Month:'))
        label.set_alignment(0, 0.5)
        months_store = Gtk.ListStore(str)
        months = calendar.month_name[1:]
        for month in months:
            months_store.append([month])
        month_combo = Gtk.ComboBox.new_with_model(months_store)
        renderer_text = Gtk.CellRendererText()
        month_combo.pack_start(renderer_text, True)
        month_combo.add_attribute(renderer_text, "text", 0)
        month_combo.set_active(int(current_time.strftime("%m"))-1)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(month_combo, True, True, 0)
        vb.pack_start(hb, True, True, 0)
        
        hb = Gtk.HBox(2)
        current_year = int(current_time.strftime("%Y"))
        adj = Gtk.Adjustment(current_year, 2000, 2020, 1, 1, 0)
        label = Gtk.Label(label=_('Year:'))
        label.set_alignment(0, 0.5)
        year_spin_button = Gtk.SpinButton() #1.0, 3
        year_spin_button.set_adjustment(adj)
        year_spin_button.set_digits(0)
        year_spin_button.set_wrap(True)
        year_spin_button.set_numeric(True)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(year_spin_button, True, True, 0)
        vb.pack_start(hb, True, True, 0)
                  
        hb = Gtk.HBox(2)
        adj = Gtk.Adjustment(10.00, 3.0, 30.0, 0.1, 1.0, 0)
        label = Gtk.Label(label=_('Frequency (MHz):'))
        label.set_alignment(0, 0.5)
        ef = Gtk.SpinButton() #1.0, 3
        ef.set_adjustment(adj)
        ef.set_digits(3)
        ef.set_wrap(True)
        ef.set_numeric(True)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(ef, True, True, 0)
        vb.pack_start(hb, True, True, 0)
        dialog.vbox.pack_start(vb, True, True, 0)
        dialog.show_all()

        ret = dialog.run()
        freq = ef.get_value()
        month = 1 + month_combo.get_active()

        interval_iter = interval_combo.get_active_iter()
        if interval_iter != None:
            model = interval_combo.get_model()
            interval = int(model[interval_iter][0])
            
        year = year_spin_button.get_value()

        dialog.destroy()
        if ret != Gtk.ResponseType.ACCEPT: return 1


        for hour in range(0, 24, interval ):
            tups.append((year, month, hour, freq))
        self.ret_templates[self.name] = tups

