
Template system
---------------


Each file must implement only one class named "templates".
This "templates" class can implement one or more templates.


The "templates" class has to define this methods:
    __init__(self, parent)
        parent is the parent window in case a dialog has to be used

    get_names(self)
        return a list of the names of the templates

    get_params(self)
        return a list of strings with properties the caller should set
        on the object. For example, for getting the parent property
        "prop" set in the templates object scope, this function must
        return ['prop']. 

    load(self)
        this is the last step performed by the caller prior to read the
        names of the templates implemented. This method should do the
        minimum amount of work because is always called in program
        start, not upon template usage.

    set_ini(self, model)
        the argument this method gets is the TreeModel object of the
        area plot tab as is at the moment the method is invoked. This
        method is called once before calling run(), so the model is
        actualized.

    run(self)
        this method is called upon the object to let it build the
        template values. It should put the result in the self.ret_templates dict,
        where the caller will retrieve the values. If a non zero value
        is returned to the caller, the procedure will be canceled, i.e.
        the template values will not be added to the model.


