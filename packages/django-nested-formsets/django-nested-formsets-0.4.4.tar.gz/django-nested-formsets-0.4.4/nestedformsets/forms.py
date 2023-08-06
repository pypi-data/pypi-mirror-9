try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from itertools import chain

from django.forms.models import ModelForm, ModelFormMetaclass

from django.forms.util import ErrorList
from django.forms.widgets import Media


class NestedModelFormOptions(object):
    def __init__(self, options=None):
        if options is None:
            return

        formsets = getattr(options, 'formsets', {})
        if isinstance(formsets, dict):
            # Support dicts for backward-compatibility reasons.
            # Order will be undefined, unless it is an OrderedDict.
            formsets = formsets.items()

        elif not isinstance(formsets, (list, tuple)):
            # Otherwise, it must be a list or tuple of (name, FormsetClass)
            raise ValueError('NestedMeta.formsets must be an list or tuple of '
                             '"(name, FormSet)" tuples')
        self.formsets = formsets

        related_forms = getattr(options, 'related_forms', ())
        if not isinstance(related_forms, (list, tuple)):
            # Otherwise, it must be a list or tuple of (name, FormsetClass)
            raise ValueError('NestedMeta.related_forms must be an list or '
                             'tuple of "(name, RelatedForm)" tuples')
        self.related_forms = related_forms


class NestedModelFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super(NestedModelFormMetaclass, cls).__new__(
            cls, name, bases, attrs)

        base_options = getattr(new_class, 'NestedMeta', None)
        new_class._nested_meta = NestedModelFormOptions(base_options)

        return new_class


class NestedModelForm(ModelForm):

    __metaclass__ = NestedModelFormMetaclass

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, formset_extra={}, related_form_extra={},
                 error_class=ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):

        super(NestedModelForm, self).__init__(
            data, files, auto_id, prefix, initial, error_class, label_suffix,
            empty_permitted, instance)

        # `self.data != data` after running __init__, so we must pass it in
        self.formsets = self._init_formsets(data, files, formset_extra)
        self.related_forms = self._init_related_forms(data, files,
                                                      related_form_extra)

    def _get_media(self):
        media_bits = chain(
            [super(NestedModelForm, self)._get_media()],
            (f.media for f in self.formsets.values()),
            (f.media for f in self.related_forms.values()))
        return sum(media_bits, Media())
    media = property(_get_media)

    @property
    def subforms(self):
        return OrderedDict(chain(self.formsets.iteritems(),
                                 self.related_forms.iteritems()))

    def _init_formsets(self, data, files, extra):
        formsets = self._nested_meta.formsets
        prefix = (self.prefix + '_') if self.prefix is not None else ''

        def make_formset(name, FormSet):
            kwargs = {
                'data': data,
                'files': files,
                'instance': self.instance,
                'prefix': prefix + name,
            }
            kwargs.update(extra.get(name, {}))
            return (name, FormSet(**kwargs))

        return OrderedDict(make_formset(name, FormSet)
                           for name, FormSet in formsets)

    def _init_related_forms(self, data, files, extra):
        related_forms = self._nested_meta.related_forms
        prefix = (self.prefix + '_') if self.prefix is not None else ''

        def make_related_form(name, RelatedForm):
            kwargs = {
                'data': data,
                'files': files,
                'instance': self.instance,
                'prefix': prefix + name,
            }
            kwargs.update(extra.get(name, {}))
            return (name, RelatedForm(**kwargs))

        return OrderedDict(make_related_form(name, RelatedForm)
                           for name, RelatedForm in related_forms)

    def is_valid(self):
        is_valid = super(NestedModelForm, self).is_valid()

        for name, subform in self.subforms.items():
            is_valid = subform.is_valid() and is_valid

        return is_valid

    def _get_formset_errors(self):
        if self._formset_errors is None:
            self.full_clean()
        return self._formset_errors
    formset_errors = property(_get_formset_errors)

    def _get_related_form_errors(self):
        if self._related_form_errors is None:
            self.full_clean()
        return self._related_form_errors
    related_form_errors = property(_get_related_form_errors)

    def full_clean(self):
        super(NestedModelForm, self).full_clean()

        self._formset_errors = {}
        for name, formset in self.formsets.items():
            if any(formset.errors):
                self._formset_errors[name] = formset.errors

        self._related_form_errors = {}
        for name, related_form in self.related_forms.items():
            if any(related_form.errors):
                self._related_form_errors[name] = related_form.errors

        if self.is_bound:
            self.post_subform_clean()

    def post_subform_clean(self):
        """ A hook for subclasses that wish to do some extra `clean()` work,
            but after the subforms have all been `clean()`ed as well.
        """
        pass

    def save(self, commit=True):

        # Prepare the instance for saving
        instance = super(NestedModelForm, self).save(commit=False)

        # Prepare the formsets for saving
        formset_instances = {}
        for name, formset in self.formsets.items():
            formset_instances[name] = (formset, formset.save(commit=False))

        # Prepare related forms for saving
        related_instances = {}
        for name, form in self.related_forms.items():
            related_instances[name] = (form, form.save(commit=False))

        # The subforms copy the instance when they are created, so they do
        # not know that this instance has just gotten a nice shiny new primary
        # key (if this is a create form, not an edit form). As such, we need to
        # loop through and tell all the related instances about our updated top
        # level instance
        def save_formsets():
            for formset, subinstances in formset_instances.values():
                fk_name = formset.fk.name
                for subinstance in subinstances:
                    setattr(subinstance, fk_name, instance)
                    subinstance.save()
                formset.save_m2m()

        def save_related_forms():
            for form, subinstance in related_instances.values():
                # The subinstance could be None, if the form was empty or the
                # instance was delete.
                if subinstance is not None:
                    fk_name = form._related_meta.fk.name
                    setattr(subinstance, fk_name, instance)
                    subinstance.save()
                    form.save_m2m()

        def save_subforms():
            save_formsets()
            save_related_forms()

        if commit:
            # Just save everything using the above helpers.
            instance.save()
            save_subforms()
            self.save_m2m()

        else:
            # if you pass `commit=False`, you have to save the formset
            # instances yourself. This helper should help.  Simply call
            # `form.save_subforms()` after you call `instance.save()`
            # Just like normal forms, if you use `commit=False` you must call
            # `form.save_m2m()` when you have saved the form and all its
            # subforms.
            self.save_formsets = save_formsets
            self.save_related_forms = save_related_forms
            self.save_subforms = save_subforms

        instances = lambda d: dict((k, v[1]) for k, v in d.iteritems())
        self.formset_instances = instances(formset_instances)
        self.related_instances = instances(related_instances)

        return instance
