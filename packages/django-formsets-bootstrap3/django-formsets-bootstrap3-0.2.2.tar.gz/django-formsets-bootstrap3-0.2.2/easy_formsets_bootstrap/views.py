from django.shortcuts import redirect
from django.core.exceptions import ValidationError


class FormsetMixin(object):
    object = None
    formsets_class = []
    is_update_view = False

    def get(self, request, *args, **kwargs):
        if getattr(self, 'is_update_view', False):
            self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets_class = self.get_formset_class()
        formsets = list(map(self.get_formset, formsets_class))
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets))

    def post(self, request, *args, **kwargs):
        if getattr(self, 'is_update_view', False):
            self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formsets = list(map(self.get_formset, formset_class))
        if form.is_valid() and [x.is_valid() for x in formsets]:
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def get_formset_class(self):
        return self.formsets_class

    def get_formset(self, formset_class):
        return formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        kwargs = {
            'instance': self.object
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def form_valid(self, form, formsets):
        self.object = form.save()
        for formset in formsets:
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form, formsets)
        if hasattr(self, 'get_success_message'):
            self.get_success_message(form)
        return redirect(self.get_succes_url())

    def form_invalid(self, form, formsets):
        return self.render_to_response(self.get_context_data(form=form, formsets=formsets))

    def get_succes_url(self):
        if self.success_url:
            url = self.success_url.format(self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url