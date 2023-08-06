from __future__ import absolute_import, unicode_literals

from six.moves import xrange

from django.db import models
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseInlineFormSet

try:
    # Django 1.6
    from django.utils.encoding import force_text as force_unicode
except ImportError:
    # Django <= 1.5
    from django.utils.encoding import force_unicode


class NestedInlineFormSetMixin(object):

    def save(self, commit=True):
        """
        Saves model instances for every form, adding and changing instances
        as necessary, and returns the list of instances.
        """
        self.changed_objects = []
        self.deleted_objects = []
        self.new_objects = []

        # Copied lines are from BaseModelFormSet.save()
        if not commit:
            self.saved_forms = []
            def save_m2m():
                for form in self.saved_forms:
                    form.save_m2m()
            self.save_m2m = save_m2m
        # End copied lines from BaseModelFormSet.save()

        # The above if clause is the entirety of BaseModelFormSet.save(),
        # along with the following return:
        # return self.save_existing_objects(commit) + self.save_new_objects(commit)

        # Iterate through self.forms and add properties `_list_position`
        # and `_is_initial` so that the forms can be put back in the
        # proper order at the end of the save method.
        #
        # We need to re-sort the forms because we can get ForeignKey
        # constraint errors if we save nested formsets in their default order.
        initial_form_count = self.initial_form_count()
        forms = []
        for i, form in enumerate(self.forms):
            form._list_position = i
            form._is_initial = bool(i < initial_form_count)
            forms.append(form)

        # Perform the sort (and allow extended logic in child classes)
        forms = self.process_forms_pre_save(forms)

        form_instances = []
        saved_instances = []

        for form in forms:
            instance = self.get_saved_instance_for_form(form, commit, form_instances)
            if instance is not None:
                # Store saved instances so we can reference it for
                # sub-instanced nested beneath not-yet-saved instances.
                saved_instances += [instance]
            else:
                instance = form.instance
            if not self._should_delete_form(form):
                form_instances.append(instance)

        # Re-sort back to original order
        saved_instances.sort(key=lambda i: i._list_position)
        return saved_instances

    def process_forms_pre_save(self, forms):
        """
        Sort by the sortable_field_name of the formset, if it has been set.

        Allows customizable sorting and modification of self.forms before
        they're iterated through in save().

        Returns list of forms.
        """
        sortable_field_name = getattr(self, 'sortable_field_name', None)
        if sortable_field_name is not None:
            default_data = {}
            default_data[sortable_field_name] = 0
            def sort_form(f):
                data = getattr(f, 'cleaned_data', default_data)
                return data.get(sortable_field_name, 0)
            forms.sort(key=sort_form)
        return forms

    def get_saved_instance_for_form(self, form, commit, form_instances=None):
        pk_name = None
        if form.instance and form.instance._meta.pk:
            pk_name = form.instance._meta.pk.name
        pk_val = None
        if not form.errors and hasattr(form, 'cleaned_data'):
            pk_val = form.cleaned_data.get(pk_name)
        # Inherited models will show up as instances of the parent in
        # cleaned_data
        if isinstance(pk_val, models.Model):
            pk_val = pk_val.pk
        if pk_val is not None:
            try:
                setattr(form.instance, pk_name, pk_val)
            except ValueError:
                pk_attname = form.instance._meta.pk.get_attname()
                setattr(form.instance, pk_attname, pk_val)

        if form._is_initial:
            instances = self.save_existing_objects([form], commit)
        else:
            instances = self.save_new_objects([form], commit)
        if len(instances):
            instance = instances[0]
            instance._list_position = form._list_position
            return instance
        else:
            return None

    def get_queryset(self):
        """
        TODO: document this extended method
        """
        if not self.data:
            return super(NestedInlineFormSetMixin, self).get_queryset()

        if not hasattr(self, '__queryset'):
            pk_keys = ["%s-%s" % (self.add_prefix(i), self.model._meta.pk.name)
                       for i in xrange(0, self.initial_form_count())]
            pk_vals = [self.data.get(pk_key) for pk_key in pk_keys if self.data.get(pk_key)]

            mgr = self.model._default_manager
            if hasattr(mgr, 'get_queryset'):
                # Django 1.6
                qs = mgr.get_queryset()
            else:
                # Django <= 1.5
                qs = mgr.get_query_set()

            qs = qs.filter(pk__in=pk_vals)

            # If the queryset isn't already ordered we need to add an
            # artificial ordering here to make sure that all formsets
            # constructed from this queryset have the same form order.
            if not qs.ordered:
                qs = qs.order_by(self.model._meta.pk.name)

            self.__queryset = qs
        return self.__queryset

    def _existing_object(self, pk):
        """
        TODO: document this extended method
        """
        if not hasattr(self, '_object_dict'):
            self._object_dict = dict([(o.pk, o) for o in self.get_queryset()])
        obj = self._object_dict.get(pk)
        if not obj:
            try:
                obj = self.model.objects.get(pk=pk)
            except self.model.DoesNotExist:
                pass
        return obj

    def _construct_form(self, i, **kwargs):
        """
        Because of the fact that existing objects can be added to inlines
        from other inlines, we sometimes get the wrong instance back.
        For instance, if an item from inline B was dragged to the top of
        inline A, and inline A already had items in it, form.instance would
        be set to the instance that was originally the first item in inline A.
        This patch fixes this problem.
        """
        form = super(NestedInlineFormSetMixin, self)._construct_form(i, **kwargs)
        pk_value = form.data.get(form.add_prefix(self._pk_field.name))
        if pk_value == '':
            pk_value = None
        if pk_value and force_unicode(form.instance.pk) != force_unicode(pk_value):
            model_cls = form.instance.__class__
            try:
                form.instance = model_cls.objects.get(pk=pk_value)
            except model_cls.DoesNotExist:
                pass
            else:
                setattr(form.instance, self.fk.get_attname(), self.instance.pk)
        return form

    def save_existing_objects(self, initial_forms=None, commit=True):
        """
        Identical to parent class, except ``self.initial_forms`` is replaced
        with ``initial_forms``, passed as parameter.
        """
        if not initial_forms:
            return []

        saved_instances = []

        if hasattr(self, 'deleted_forms'):
            # Django 1.6
            forms_to_delete = self.deleted_forms
        else:
            # Django <= 1.5
            forms_to_delete = [f for f in initial_forms
                               if self.can_delete and self._should_delete_form(f)]

        for form in initial_forms:
            pk_name = self._pk_field.name
            raw_pk_value = form._raw_value(pk_name)

            # clean() for different types of PK fields can sometimes return
            # the model instance, and sometimes the PK. Handle either.
            if self._should_delete_form(form):
                pk_value = raw_pk_value
            else:
                pk_value = form.fields[pk_name].clean(raw_pk_value)
                pk_value = getattr(pk_value, 'pk', pk_value)

            obj = None
            if obj is None and form.instance and pk_value:
                model_cls = form.instance.__class__
                try:
                    obj = model_cls.objects.get(pk=pk_value)
                except model_cls.DoesNotExist:
                    if pk_value and force_unicode(form.instance.pk) == force_unicode(pk_value):
                        obj = form.instance
            if obj is None:
                obj = self._existing_object(pk_value)

            if form in forms_to_delete:
                self.deleted_objects.append(obj)
                obj.delete()
                continue

            # fk_val: The value one should find in the form's foreign key field
            new_ct_val = ct_val = ContentType.objects.get_for_model(self.instance.__class__)
            new_fk_val = fk_val = self.instance.pk
            if form.instance.pk:
                original_instance = self.model.objects.get(pk=form.instance.pk)
                fk_field = getattr(self, 'fk', getattr(self, 'ct_fk_field', None))
                if fk_field:
                    new_fk_val = getattr(original_instance, fk_field.get_attname())
                ct_field = getattr(self, 'ct_field', None)
                if ct_field:
                    new_ct_val = getattr(original_instance, ct_field.get_attname())

            if form.has_changed() or fk_val != new_fk_val or ct_val != new_ct_val:
               self.changed_objects.append((obj, form.changed_data))
               saved_instances.append(self.save_existing(form, obj, commit=commit))
               if not commit:
                   self.saved_forms.append(form)
        return saved_instances

    def save_new_objects(self, extra_forms=None, commit=True):
        """
        Identical to parent class, except ``self.extra_forms`` is replaced
        with ``extra_forms``, passed as parameter, and self.new_objects is
        replaced with ``new_objects``.
        """
        new_objects = []

        if extra_forms is None:
            return new_objects

        for form in extra_forms:
            if not form.has_changed():
                continue
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue
            new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)

        self.new_objects.extend(new_objects)
        return new_objects


class NestedInlineFormSet(NestedInlineFormSetMixin, BaseInlineFormSet):
    """
    The nested InlineFormSet for the common case (ForeignKey inlines)
    """
    pass


class GenericNestedInlineFormSet(NestedInlineFormSetMixin, BaseGenericInlineFormSet):
    """
    The nested InlineFormSet for inlines of generic content-type relations
    """

    @classmethod
    def get_default_prefix(cls):
        opts = cls.model._meta
        return '-'.join((opts.app_label, opts.object_name.lower(),
                        cls.ct_field.name, cls.ct_fk_field.name))

