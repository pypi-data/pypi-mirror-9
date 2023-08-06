from frasco import Feature, action, signal, current_app, request, current_context
from frasco.utils import AttrDict, DictObject
from jinja2 import FileSystemLoader
import os
import inspect
from .form import *


class FormsFeature(Feature):
    """Create and use forms using wtforms.
    """
    name = "forms"
    defaults = {"import_macros": True,
                "csrf_enabled": True}

    form_validation_failed_signal = signal("form_validation_failed")
    form_submitted_signal = signal("form_submitted")
    form_created_from_view_signal = signal("form_created_from_view")

    def init_app(self, app):
        self.forms = {}
        if self.options["import_macros"]:
            macro_file = os.path.join(os.path.dirname(__file__), "macros.html")
            app.jinja_env.macros.register_file(macro_file, "form.html")
            app.jinja_env.macros.alias("form_tag", "form")

    def init_declarative(self, app):
        self.load_forms_from_templates(app)

    def load_forms_from_templates(self, app, folder="forms", prefix="__forms__"):
        path = os.path.join(app.root_path, folder)
        if os.path.exists(path):
            app.jinja_env.loader.add_prefix(prefix, FileSystemLoader(path))
            for form_class in FormLoader(path, prefix).load(app):
                self.register(form_class)

    def register(self, form_class):
        self.forms[form_class.__name__] = form_class
        return form_class

    def __getitem__(self, name):
        return self.forms[name]

    def __setitem__(self, name, form):
        self.forms[name] = form

    def __contains__(self, name):
        return name in self.forms

    @action(default_option="form", methods=("GET", "POST"), as_="form")
    def form(self, obj=None, form=None, name=None, template=None, var_name=None, validate_on_submit=True,\
        exit_on_failure=True, csrf_enabled=None):
        """Loads a form and validates it (unless specified).
        If the form referenced has not been loaded, an attempt to create a form
        object using the information in the template will be made.
        """
        if not form or isinstance(form, str):
            if not name and isinstance(form, str):
                name = form
            if not name:
                name = request.endpoint.rsplit('.', 1)[1] if '.' in request.endpoint else request.endpoint
            if name not in self.forms:
                raise NoFormError("Cannot find form '%s'" % name)
            form = self.forms[name]
        if inspect.isclass(form):
            if isinstance(obj, dict):
                obj = DictObject(obj)
            if csrf_enabled is None:
                csrf_enabled = self.options["csrf_enabled"]
            form = form(obj=obj, csrf_enabled=csrf_enabled)

        current_context.data.form = form
        yield form

        if validate_on_submit and request.method == "POST":
            self.validate(form, exit_on_failure=exit_on_failure)

    @action("create_form_from_view", default_option="name", as_="form_class")
    def create_from_view(self, name=None, template=None, var_name=None):
        if not name:
            name = request.endpoint.rsplit('.', 1)[1] if '.' in request.endpoint else request.endpoint
        return self.forms[name]

    @create_from_view.init_view
    @form.init_view
    def init_form_view(self, view, opts):
        """Checks if the form referenced in the view exists or attempts to
        create it by parsing the template
        """
        name = opts.get("name", opts.get("form"))
        if isinstance(name, Form):
            return

        template = opts.get("template", getattr(view, "template", None))
        if not template:
            if not name:
                raise NoFormError("No form name specified in the form action and no template")
            return

        try:
            as_ = opts.get("var_name", getattr(self.form, "as_", "form"))
            form_class = create_from_template(current_app, template, var_name=as_)
        except NoFormError:
            if not name:
                raise
            return

        if not name:
            name = view.name

        self.forms[name] = form_class
        self.form_created_from_view_signal.send(self, view=view, form_class=form_class)
        return form_class

    @action("create_form_from_template", as_="form_class")
    def create_from_template(self, name, template, var_name="form"):
        form_class = create_from_template(current_app, template, var_name=var_name)
        self.forms[name] = form_class
        return form_class

    @action("validate_form")
    def validate(self, form=None, return_success=False, exit_on_failure=True):
        ctx = current_context
        if not form:
            form = ctx.data.form
        if not form.validate():
            self.form_validation_failed_signal.send(self, form=form)
            if exit_on_failure:
                ctx.exit(trigger_action_group="form_validation_failed")
            ctx.trigger_action_group("form_validation_failed")
        self.form_submitted_signal.send(self, form=form)
        if not return_success:
            ctx.trigger_action_group("form_submitted")
        return True

    @action("form_to_obj")
    def populate_obj(self, obj=None, form=None):
        """Populates an object with the form's data
        """
        if not form:
            form = current_context.data.form
        if obj is None:
            obj = AttrDict()
        form.populate_obj(obj)
        return obj