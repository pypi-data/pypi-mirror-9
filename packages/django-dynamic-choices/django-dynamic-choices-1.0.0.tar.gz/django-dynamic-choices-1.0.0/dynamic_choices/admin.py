import json
from functools import update_wrapper

import django
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.forms.models import ModelForm, _get_foreign_key, model_to_dict
from django.forms.widgets import Select, SelectMultiple
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.template.base import FilterExpression
from django.template.defaultfilters import escape
from django.template.loader import get_template
from django.template.loader_tags import ExtendsNode
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.utils.safestring import SafeUnicode

from .compat import get_model_name
from .forms import DynamicModelForm, dynamic_model_form_factory
from .forms.fields import DynamicModelChoiceField

try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError:
    from django.db.models.sql.constants import LOOKUP_SEP


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return super(LazyEncoder, self).default(obj)

lazy_encoder = LazyEncoder()


def get_dynamic_choices_from_form(form):
    fields = {}
    if form.prefix:
        prefix = "%s-%s" % (form.prefix, '%s')
    else:
        prefix = '%s'
    for name, field in form.fields.iteritems():
        if isinstance(field, DynamicModelChoiceField):
            widget_cls = field.widget.widget.__class__
            if widget_cls in (Select, SelectMultiple):
                widget = 'default'
            else:
                widget = "%s.%s" % (widget_cls.__module__,
                                    widget_cls.__name__)
            fields[prefix % name] = {
                'widget': widget,
                'value': list(field.widget.choices)
            }
    return fields


def dynamic_formset_factory(fieldset_cls, initial):
    class cls(fieldset_cls):
        if django.VERSION >= (1, 6):
            def __init__(self, *args, **kwargs):
                super(cls, self).__init__(*args, **kwargs)
                store = getattr(self, 'initial', None)
                if store is None:
                    store = []
                    setattr(self, 'initial', store)
                for i in xrange(self.total_form_count()):
                    try:
                        actual = store[i]
                        actual.update(initial)
                    except (ValueError, IndexError):
                        store.insert(i, initial)
        else:
            def _construct_forms(self):
                "Append initial data for every single form"
                store = getattr(self, 'initial', None)
                if store is None:
                    store = []
                    setattr(self, 'initial', store)
                for i in xrange(self.total_form_count()):
                    try:
                        actual = store[i]
                        actual.update(initial)
                    except (ValueError, IndexError):
                        store.insert(i, initial)
                return super(cls, self)._construct_forms()

        @property
        def empty_form(self):
            form = self.form(
                auto_id=self.auto_id,
                prefix=self.add_prefix('__prefix__'),
                empty_permitted=True,
                initial=initial,
            )
            self.add_fields(form, None)
            return form

    cls.__name__ = "Dynamic%s" % fieldset_cls.__name__
    return cls


def dynamic_inline_factory(inline_cls):
    "Make sure the inline has a dynamic form"
    form_cls = getattr(inline_cls, 'form', None)
    if form_cls is ModelForm:
        form_cls = DynamicModelForm
    elif issubclass(form_cls, DynamicModelForm):
        return inline_cls
    else:
        form_cls = dynamic_model_form_factory(form_cls)

    class cls(inline_cls):
        form = form_cls

        def get_formset(self, request, obj=None, **kwargs):
            formset = super(cls, self).get_formset(request, obj=None, **kwargs)
            if not isinstance(formset.form(), DynamicModelForm):
                raise Exception('DynamicAdmin inlines\'s formset\'s form must be an instance of DynamicModelForm')
            return formset

    cls.__name__ = "Dynamic%s" % inline_cls.__name__
    return cls


def template_extends(template_name, expected_parent_name):
    template = get_template(template_name)
    if (len(template.nodelist) and
            isinstance(template.nodelist[0], ExtendsNode)):
        node = template.nodelist[0]
        parent_name = node.parent_name
        # As of django 1.4, parent_name is a FilterExpression
        if isinstance(parent_name, FilterExpression):
            parent_name = parent_name.resolve({})
        if parent_name == expected_parent_name:
            return True
        else:
            return template_extends(parent_name, expected_parent_name)
    else:
        return False


def dynamic_admin_factory(admin_cls):

    change_form_template = 'admin/dynamic_choices/change_form.html'

    class meta_cls(type(admin_cls)):

        "Metaclass that ensure form and inlines are dynamic"
        def __new__(cls, name, bases, attrs):
            # If there's already a form defined we make sure to subclass it
            if 'form' in attrs:
                attrs['form'] = dynamic_model_form_factory(attrs['form'])
            else:
                attrs['form'] = DynamicModelForm

            # Make sure the specified add|change_form_template
            # extends "admin/dynamic_choices/change_form.html"
            for t, default in {'add_form_template': None,
                               'change_form_template': change_form_template}.iteritems():
                if t in attrs:
                    if not template_extends(attrs[t], change_form_template):
                        raise ImproperlyConfigured("Make sure specified %s.%s='%s' template extends '%s' "
                                                   "in order to enable DynamicAdmin" % (name, t, attrs[t],
                                                                                        change_form_template))
                else:
                    attrs[t] = default

            # If there's some inlines defined we make sure that their form is dynamic
            # see dynamic_inline_factory
            if 'inlines' in attrs:
                attrs['inlines'] = [dynamic_inline_factory(inline_cls) for inline_cls in attrs['inlines']]

            return super(meta_cls, cls).__new__(cls, name, bases, attrs)

    class cls(admin_cls):

        __metaclass__ = meta_cls

        def _media(self):
            media = super(cls, self).media
            media.add_js(('js/dynamic-choices.js',
                          'js/dynamic-choices-admin.js'))
            return media
        media = property(_media)

        def get_urls(self):
            def wrap(view):
                def wrapper(*args, **kwargs):
                    return self.admin_site.admin_view(view)(*args, **kwargs)
                return update_wrapper(wrapper, view)

            info = self.model._meta.app_label, get_model_name(self.model._meta)

            urlpatterns = [
                url(r'(?:add|(?P<object_id>\w+))/choices/$',
                    wrap(self.dynamic_choices),
                    name="%s_%s_dynamic_admin" % info),
            ] + super(cls, self).get_urls()

            return urlpatterns

        def get_dynamic_choices_binder(self, request):

            def id(field):
                return "[name='%s']" % field

            def inline_field_selector(fieldset, field):
                return "[name^='%s-'][name$='-%s']" % (fieldset, field)

            fields = {}

            def add_fields(to_fields, to_field, bind_fields):
                if not (to_field in to_fields):
                    to_fields[to_field] = set()
                to_fields[to_field].update(bind_fields)

            model_name = get_model_name(self.model._meta)

            # Use get_form in order to allow formfield override
            # We should create a fake request from referer but all this
            # hack will be fixed when the code is embed directly in the page
            form = self.get_form(request)()
            rels = form.get_dynamic_relationships()
            for rel in rels:
                field_name = rel.split(LOOKUP_SEP)[0]
                if rel in form.fields:
                    add_fields(fields, id(field_name), [id(field) for field in rels[rel] if field in form.fields])

            inlines = {}
            for formset in self.get_formsets(request):
                inline = {}
                formset_form = formset.form()
                inline_rels = formset_form.get_dynamic_relationships()
                prefix = formset.get_default_prefix()
                for rel in inline_rels:
                    if LOOKUP_SEP in rel:
                        base, field = rel.split(LOOKUP_SEP)[0:2]
                        if base == model_name and field in form.fields:
                            bound_fields = [
                                inline_field_selector(prefix, f)
                                for f in inline_rels[rel] if f in formset_form.fields
                            ]
                            add_fields(fields, id(field), bound_fields)
                        elif base in formset_form.fields:
                            add_fields(inline, base, inline_rels[rel])
                    elif rel in formset_form.fields:
                        add_fields(inline, rel, inline_rels[rel])
                if len(inline):
                    inlines[prefix] = inline

            # Replace sets in order to allow JSON serialization
            for field, bindeds in fields.iteritems():
                fields[field] = list(bindeds)

            for fieldset, inline_fields in inlines.iteritems():
                for field, bindeds in inline_fields.iteritems():
                    inlines[fieldset][field] = list(bindeds)

            return SafeUnicode(u"django.dynamicAdmin(%s, %s);" % (json.dumps(fields),
                                                                  json.dumps(inlines)))

        def dynamic_choices(self, request, object_id=None):

            opts = self.model._meta
            obj = self.get_object(request, object_id)
            # Make sure the specified object exists
            if object_id is not None and obj is None:
                raise Http404('%(name)s object with primary key %(key)r does not exist.' % {
                              'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

            form = self.get_form(request)(request.GET, instance=obj)
            data = get_dynamic_choices_from_form(form)

            for formset in self.get_formsets(request, obj):
                prefix = formset.get_default_prefix()
                try:
                    fs = formset(request.GET, instance=obj)
                    forms = fs.forms + [fs.empty_form]
                except ValidationError:
                    return HttpResponseBadRequest("Missing %s ManagementForm data" % prefix)
                for form in forms:
                    data.update(get_dynamic_choices_from_form(form))

            if 'DYNAMIC_CHOICES_FIELDS' in request.GET:
                fields = request.GET.get('DYNAMIC_CHOICES_FIELDS').split(',')
                for field in data.keys():
                    if not (field in fields):
                        del data[field]

            return HttpResponse(lazy_encoder.encode(data), content_type='application/json')

        # Make sure to pass request data to fieldsets
        # so they can use it to define choices
        def get_formsets(self, request, obj=None):
            initial = {}
            model = self.model
            opts = model._meta
            data = getattr(request, request.method).items()
            # If an object is provided we collect data
            if obj is not None:
                initial.update(model_to_dict(obj))
            # Make sure to collect parent model data
            # and provide it to fieldsets in the form of
            # parent__field from request if its provided.
            # This data should be more "up-to-date".
            for k, v in data:
                if v:
                    try:
                        f = opts.get_field(k)
                    except models.FieldDoesNotExist:
                        continue
                    if isinstance(f, models.ManyToManyField):
                        initial[k] = v.split(",")
                    else:
                        initial[k] = v

            try:
                # Django >= 1.4
                inline_instances = self.get_inline_instances(request)
            except AttributeError:
                # Django < 1.4
                inline_instances = self.inline_instances

            for formset, inline in zip(super(cls, self).get_formsets(request, obj), inline_instances):
                fk = _get_foreign_key(self.model, inline.model, fk_name=inline.fk_name).name
                fk_initial = dict(('%s__%s' % (fk, k), v) for k, v in initial.iteritems())
                # If we must provide additional data
                # we must wrap the formset in a subclass
                # because passing 'initial' key argument is intercepted
                # and not provided to subclasses by BaseInlineFormSet.__init__
                if len(initial):
                    formset = dynamic_formset_factory(formset, fk_initial)
                yield formset

        def add_view(self, request, form_url='', extra_context=None):
            context = {'dynamic_choices_binder': self.get_dynamic_choices_binder(request)}
            context.update(extra_context or {})
            return super(cls, self).add_view(request, form_url='', extra_context=context)

        def change_view(self, request, object_id, extra_context=None):
            context = {'dynamic_choices_binder': self.get_dynamic_choices_binder(request)}
            context.update(extra_context or {})
            return super(cls, self).change_view(request, object_id, extra_context=context)

    return cls

DynamicAdmin = dynamic_admin_factory(admin.ModelAdmin)

try:
    from reversion.admin import VersionAdmin
    DynamicVersionAdmin = dynamic_admin_factory(VersionAdmin)
except ImportError:
    pass
