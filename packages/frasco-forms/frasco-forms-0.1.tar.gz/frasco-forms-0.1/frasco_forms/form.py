from flask_wtf import Form as WTForm
import wtforms.fields as wtfields
import wtforms.fields.html5 as wtfields5
import wtforms.validators as wtvalidators
from frasco import Markup, render_template, AttrDict, translate, ntranslate, lazy_translate
from frasco.templating import parse_template, jinja_node_to_python
from frasco.declarative import FileLoader
from jinja2 import nodes
import inflection
import os


__all__ = ('Form', 'TemplateForm', 'fields', 'validators', 'FormDefinitionError',
           'NoFormError', 'FormLoader', 'create_from_template')


field_type_map = {"checkbox": wtfields.BooleanField,
                  "decimal": wtfields.DecimalField,
                  "date": wtfields.DateField,
                  "datetime": wtfields.DateTimeField,
                  "float": wtfields.FloatField,
                  "int": wtfields.IntegerField,
                  "radio": wtfields.RadioField,
                  "select": wtfields.SelectField,
                  "selectmulti": wtfields.SelectMultipleField,
                  "text": wtfields.StringField,
                  "textarea": wtfields.TextAreaField,
                  "password": wtfields.PasswordField,
                  "hidden": wtfields.HiddenField,
                  "date5": wtfields5.DateField,
                  "datetime5": wtfields5.DateTimeField,
                  "datetimelocal": wtfields5.DateTimeLocalField,
                  "decimal5": wtfields5.DecimalField,
                  "decimalrange": wtfields5.DecimalRangeField,
                  "email": wtfields5.EmailField,
                  "int5": wtfields5.IntegerField,
                  "intrange": wtfields5.IntegerRangeField,
                  "search": wtfields5.SearchField,
                  "tel": wtfields5.TelField,
                  "url": wtfields5.URLField}


# for easy import
fields = AttrDict(field_type_map)
validators = wtvalidators


class FormTranslations(object):
    def gettext(self, string, **kwargs):
        return translate(string, **kwargs)

    def ngettext(self, singular, plural, n, **kwargs):
        return ntranslate(singular, plural, n, **kwargs)


class Form(WTForm):
    @property
    def enctype(self):
        for f in self:
            if f.type == "FileField":
                return "multipart/form-data"
        return "application/x-www-form-urlencoded"

    def populate_obj(self, obj, ignore_fields=None):
        for name, field in self._fields.iteritems():
            if not ignore_fields or name not in ignore_fields:
                field.populate_obj(obj, name)

    def _get_translations(self):
        return FormTranslations()


class TemplateForm(Form):
    """Wraps the form object to make it easer to build and access form from
    context variables and templates. Access to undefined attributes will
    return a function which when called will return the field which name
    matches the fist argument. All other arguments are ignored.
    """
    template = None

    def __init__(self, template=None, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        if template:
            self.template = template

    def render(self, **kwargs):
        return render_template(self.template, form=self, **kwargs)

    def __call__(self, **kwargs):
        return Markup(self.render(**kwargs))


def _fake_field_init(field):
    def caller(*args, **kwargs):
        return field
    return caller


class TemplateField(object):
    _formfield = True

    def __init__(self, field):
        object.__setattr__(self, "_field", field)

    def __getattr__(self, name):
        if hasattr(self._field, name):
            return getattr(self._field, name)
        if name in field_type_map:
            return _fake_field_init(self._field)
        raise AttributeError

    def __setattr__(self, name, value):
        setattr(self._field, name, value)

    def __call__(self, *args, **kwargs):
        return self._field(*args, **kwargs)


class UnboundTemplateField(TemplateField):
    def bind(self, *args, **kwargs):
        return TemplateField(self._field.bind(*args, **kwargs))


class FormDefinitionError(Exception):
    pass


class NoFormError(Exception):
    pass


class FormLoader(FileLoader):
    def __init__(self, path, base_template_path="", **kwargs):
        super(FormLoader, self).__init__(path, **kwargs)
        self.base_template_path = base_template_path

    def load_file(self, app, pathname, relpath, pypath):
        name, _ = os.path.splitext(os.path.basename(pathname))
        return create_from_template(app, os.path.join(self.base_template_path, relpath), name)


def create_from_template(app, filename, *args, **kwargs):
    node = parse_template(app, filename)
    form_class = create_from_template_node(node, *args, **kwargs)
    form_class.template = filename
    return form_class


def create_from_template_node(template_node, name="F", var_name="form"):
    # The parsing process looks for Call nodes applied on a GetAttr node
    # where the target is the form variable. The form variable name is "form"
    # by default but can be overrided by the "as" option
    fields = {}
    for call in template_node.find_all((nodes.Call,)):
        if not isinstance(call.node, nodes.Getattr) or not isinstance(call.node.node, nodes.Getattr):
            continue
        attrnode = call.node.node
        if not isinstance(attrnode.node, nodes.Name) or not attrnode.node.name == var_name:
            continue
        fname = attrnode.attr
        fields[fname] = [call.node.attr, {}]

        if len(call.args) > 0:
            fields[fname][1]["label"] = _check_translation(call.args[0])

        for arg in call.kwargs:
            fields[fname][1][arg.key] = _check_translation(arg.value)

    form_class = type(name, (TemplateForm,), {"name": name})

    for fname, fopts in fields.iteritems():
        ftype, kwargs = fopts
        if ftype not in field_type_map:
            raise FormDefinitionError("Unknown field type '%s'" % ftype)
        validators = []
        if "label" not in kwargs:
            kwargs["label"] = inflection.humanize(fname)
        if kwargs.pop("required", False):
            if ftype == "file":
                validators.append(FileRequired())
            else:
                validators.append(wtvalidators.DataRequired())
        if kwargs.pop("optional", False):
            validators.append(wtvalidators.Optional())
        if "range" in kwargs:
            min, max = kwargs.pop("range")
            validators.append(wtvalidators.NumberRange(min, max))
        if "length" in kwargs:
            min, max = kwargs.pop("length")
            validators.append(wtvalidators.Length(min, max))
        if "validators" in kwargs:
            for v in kwargs.pop("validators"):
                validators.append(getattr(wtvalidators, v)())
        setattr(form_class, fname, UnboundTemplateField(field_type_map[ftype](validators=validators, **kwargs)))

    return form_class


def _check_translation(node):
    if isinstance(node, nodes.Call):
        if not isinstance(node.node, nodes.Name) or node.node.name not in ("_", "translate", "gettext"):
            raise FormDefinitionError("Cannot use a function call (other than translation calls) in field definitions")
        return lazy_translate(jinja_node_to_python(node.args[0]))
    return jinja_node_to_python(node)