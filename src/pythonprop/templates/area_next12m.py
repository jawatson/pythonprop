
import area_nextmonths as mod

class templates(mod.templates):

    name = 'Next 12 Months'
    description = 'Following 12 months after the last in the list, or next 12 months from today if the list is empty.'

    def __init__(self, parent):
        mod.templates.__init__(self, parent)
        mod.templates.iter = 12


