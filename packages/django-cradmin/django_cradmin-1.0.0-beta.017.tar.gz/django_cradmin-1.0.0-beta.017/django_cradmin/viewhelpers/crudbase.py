import urllib
from django import forms
from django import http
from django.contrib import messages
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from crispy_forms import layout

from . import formbase


class CreateUpdateViewMixin(formbase.FormViewMixin):
    """
    Mixin class for Update and Create views.
    """

    #: The model class.
    model = None

    #: List of field names.
    #: See :meth:`.get_field_layout`.
    fields = None

    #: The name of the submit button used for preview.
    #: Only used when :meth:`.preview_url` is defined.
    submit_preview_name = 'submit-preview'

    #: The field that should always be set to the current role.
    #: Removes the field from the form (see :meth:`.get_form`),
    #: and instead sets the value directly on the object in
    #: :meth:`.save_object`.
    roleid_field = None

    #: The viewname within this app for the edit view.
    #: See :meth:`.get_editurl`.
    editview_appurl_name = 'edit'

    def get_field_layout(self):
        """
        Get a list/tuple of fields. These are added to a ``crispy_forms.layout.Layout``.
        Defaults to a all fields on the model. If :obj:`.fields`, we use those fields.

        Simple example (same as specifying the fields in :obj:`.fields`)::

            from crispy_forms import layout

            class MyCreateView(CreateView):
                def get_field_layout(self):
                    return [
                        layout.Div(
                            'title', 'name', 'size', 'tags',
                            css_class='cradmin-globalfields')
                    ]

        A slightly more complex example::

            from crispy_forms import layout

            class MyCreateView(CreateView):
                def get_field_layout(self):
                    return [
                        layout.Div('title', css_class="cradmin-focusfield cradmin-focusfield-lg"),
                        layout.Div('description', css_class="cradmin-focusfield"),
                        layout.Fieldset('Metadata',
                            'size',
                            'tags'
                        )

                    ]

        """
        fields = forms.fields_for_model(self.model, fields=self.fields).keys()
        if self.roleid_field and self.roleid_field in fields:
            fields.remove(self.roleid_field)
        return [layout.Div(*fields, css_class='cradmin-globalfields')]

    def get_form(self, form_class):
        """
        If you set :obj:`.roleid_field`, we will remove that field from
        the form.

        .. note::
            The :obj:`.roleid_field` handling also works for GenericForeignKey
            fields (removes the content type and object pk field from the form).
        """
        form = super(CreateUpdateViewMixin, self).get_form(form_class)
        if self.roleid_field:
            roleid_fieldobject = getattr(self.model, self.roleid_field, None)
            if isinstance(roleid_fieldobject, GenericForeignKey):
                for fieldname in roleid_fieldobject.fk_field, roleid_fieldobject.ct_field:
                    if fieldname in form.fields:
                        del form.fields[fieldname]
            else:
                if self.roleid_field in form.fields:
                    del form.fields[self.roleid_field]
        return form

    def get_context_data(self, **kwargs):
        context = super(CreateUpdateViewMixin, self).get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        if getattr(self, 'show_preview', False):
            context['preview_url'] = self.get_preview_url()
            context['show_preview'] = True
        return context

    def get_editurl(self, obj):
        """
        Get the edit URL for ``obj``.

        Defaults to::

            self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])
        """
        return self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])

    def _get_full_editurl(self, obj):
        url = self.get_editurl(obj)
        if 'success_url' in self.request.GET:
            url = '{}?{}'.format(
                url, urllib.urlencode({
                    'success_url': self.request.GET['success_url']}))
        return url

    def get_success_url(self):
        if 'submit-save-and-continue-editing' in self.request.POST:
            return self._get_full_editurl(self.object)
        else:
            return self.get_default_save_success_url()

    def save_object(self, form, commit=True):
        """
        Save the object. You can override this to customize how the
        form is turned into a saved object.

        Make sure you call ``super`` if you override this (see the docs for the commit parameter).
        If you do not, you will loose the automatic handling of obj:`.roleid_field`.

        Parameters:
            commit (boolean): If this is ``False``, the object is returned
                unsaved. Very useful when you want to manipulate the object
                before saving it in a subclass.

        Returns:
            The saved object.
        """
        obj = form.save(commit=False)
        if self.roleid_field:
            setattr(obj, self.roleid_field, self.request.cradmin_role)
        if commit:
            obj.save()
        return obj

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if self.preview_requested():
            self._store_preview_in_session(self.serialize_preview(form))
            self.show_preview = True
            return self.render_to_response(self.get_context_data(form=form))
        else:
            self.object = self.save_object(form)
            self.form_saved(self.object)
            self.add_success_messages(self.object)
            return http.HttpResponseRedirect(self.get_success_url())

    def form_saved(self, object):
        """
        Called after the form has been successfully saved.
        The ``object`` is the saved object.

        Does nothing by default, but you can override it if you need to
        do something extra post save.
        """
        pass

    def get_success_message(self, object):
        """
        Override this to provide a success message.

        The ``object`` is the saved object.

        Used by :meth:`.add_success_messages`.
        """
        return None

    def add_success_messages(self, object):
        """
        Called after the form has been saved, and after :meth:`.form_saved` has been called.

        The ``object`` is the saved object.

        Defaults to add :meth:`.get_success_message` as a django messages
        success message if :meth:`.get_success_message` returns anything.

        You can override this to add multiple messages or to show messages in some other way.
        """
        success_message = self.get_success_message(object)
        if success_message:
            messages.success(self.request, success_message)

    def get_form_invalid_message(self, form):
        """
        You can override this to provide a custom error message.

        Defaults to "Please fix the errors in the form below.".

        The ``form`` is the invalid form object.

        Used by :meth:`.add_form_invalid_messages`.
        """
        return _('Please fix the errors in the form below.')

    def add_form_invalid_messages(self, form):
        """
        Called to add messages when the form does not validate.

        The ``form`` is the invalid form object.

        Defaults to add :meth:`.get_form_invalid_message` as a django messages
        error message if :meth:`.get_form_invalid_message` returns anything.

        You can override this to add multiple messages or to show error messages in some other way.
        """
        form_invalid_message = self.get_form_invalid_message(object)
        if form_invalid_message:
            messages.error(self.request, form_invalid_message)

    def form_invalid(self, form):
        self.add_form_invalid_messages(form)
        return super(CreateUpdateViewMixin, self).form_invalid(form)

    def preview_requested(self):
        """
        Determine if a preview was requested.

        Defaults to checking if :obj:`.submit_preview_name` is
        in ``request.POST``.
        """
        return self.submit_preview_name in self.request.POST

    def get_preview_url(self):
        """
        Get the URL of the preview view.
        """
        return None

    def _store_preview_in_session(self, data):
        self.request.session[self.__class__.get_preview_sessionkey()] = data

    def serialize_preview(self, form):
        """
        Seralize for preview.

        Defaults to serializing the object as JSON using ``django.core.serializers``.
        You can safely override this, but you will also have to override
        :meth:`deserialize_preview`.
        """
        return serializers.serialize('json', [self.save_object(form, commit=False)])

    @classmethod
    def deserialize_preview(self, serialized):
        """
        Deseralize a preview serialized with :meth:`.serialize_preview`.
        """
        return list(serializers.deserialize('json', serialized))[0].object

    @classmethod
    def get_preview_sessionkey(cls):
        """
        Get the session key used for preview. You should not
        need to override this.
        """
        return 'django_cradmin__{module}.{classname}'.format(
            module=cls.model.__module__,
            classname=cls.model.__name__)

    @classmethod
    def get_preview_data(cls, request):
        """
        Get the preview data.

        You should use this in the preview view to get the
        data for the preview.

        You normally do not override this. If you want to manage
        serialization yourself, see :meth:`.serialize_preview`.
        """
        serialized = request.session.pop(cls.get_preview_sessionkey())
        return cls.deserialize_preview(serialized)
