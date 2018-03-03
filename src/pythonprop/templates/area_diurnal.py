
from gi.repository import Gtk
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

# Template to run an area prediction at predefined hourly interval through a single day

class templates:
    name = 'Diurnal'

    def __init__(self, parent, ssn_repo):
        self.parent = parent
        self.ssn_repo = ssn_repo
        self.ret_templates = {} # { templatename : [(month_i,utc,freq),...]}
        self.year_spin_button = Gtk.SpinButton() #1.0, 3
        self.month_combo = Gtk.ComboBox()



    def get_names(self):
        return [self.name,]

    def get_params(self):
        return []

    def load(self):
        return

    def set_ini(self, model):
        pass

    def update_month_spin_range(self,widget):
        """
        Called when the year changes and modifies the months range to values
        that are in the ssn_repo.
        """
        _min, _max = self.ssn_repo.get_data_range()
        active_month = self.month_combo.get_active()
        if (self.year_spin_button.get_value_as_int() == _min.year):
            min_month = _min.month
            max_month = 12
            active_month = max(active_month - min_month + 1, 0)
        elif (self.year_spin_button.get_value_as_int() == _max.year):
            min_month = 1
            max_month = _max.month
            active_month = min(active_month, min_month)
        else:
            min_month = 1
            max_month = 12

        months_store = self.month_combo.get_model()
        months_store.clear()
        for month in calendar.month_name[min_month:max_month+1]:
            months_store.append([month])
        self.month_combo.set_model(months_store)
        self.month_combo.set_active(active_month)


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
        renderer_text = Gtk.CellRendererText()
        self.month_combo.set_model(months_store)
        self.month_combo.pack_start(renderer_text, True)
        self.month_combo.add_attribute(renderer_text, "text", 0)
        self.month_combo.set_active(int(current_time.strftime("%m"))-1)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(self.month_combo, True, True, 0)
        vb.pack_start(hb, True, True, 0)

        hb = Gtk.HBox(2)
        current_year = int(current_time.strftime("%Y"))
        adj = Gtk.Adjustment(current_year, 2000, 2020, 1, 1, 0)
        label = Gtk.Label(label=_('Year:'))
        label.set_alignment(0, 0.5)
        self.year_spin_button.set_adjustment(adj)
        self.year_spin_button.set_digits(0)
        self.year_spin_button.set_wrap(False)
        self.year_spin_button.set_numeric(True)
        self.year_spin_button.set_value(current_year)
        _min, _max = self.ssn_repo.get_data_range()
        self.year_spin_button.set_range(_min.year, _max.year)
        year_spin_updated_handler_id = self.year_spin_button.connect("value-changed", self.update_month_spin_range)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(self.year_spin_button, True, True, 0)
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
        ef.set_value(7.1)
        hb.pack_start(label, True, True, 0)
        hb.pack_end(ef, True, True, 0)
        vb.pack_start(hb, True, True, 0)
        dialog.vbox.pack_start(vb, True, True, 0)
        dialog.show_all()

        ret = dialog.run()
        freq = ef.get_value()
        month = 1 + self.month_combo.get_active()

        interval_iter = interval_combo.get_active_iter()
        if interval_iter != None:
            model = interval_combo.get_model()
            interval = int(model[interval_iter][0])

        year = self.year_spin_button.get_value()

        dialog.destroy()
        if ret != Gtk.ResponseType.ACCEPT: return 1


        for hour in range(0, 24, interval ):
            tups.append((year, month, hour, freq))
        self.ret_templates[self.name] = tups
