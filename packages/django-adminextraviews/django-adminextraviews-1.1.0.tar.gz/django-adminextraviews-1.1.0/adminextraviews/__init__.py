import pkg_resources
from functools import partial

from django import forms
from django.views.generic.edit import ModelFormMixin
from django.forms.models import modelform_factory

__version__ = pkg_resources.get_distribution('django-adminextraviews').version


class ExtraViewsMixin(object):
    """
    A ModelAdmin mixin for adding extra class-based views.

    Usage:

        class MyModelAdmin(ExtraViewsMixin, admin.ModelAdmin):
            extra_views = [
                ('login_as_user', r'(?P<pk>\d+)/login/', LoginAsUserView),
            ]
    """
    extra_views = []

    def get_extra_views(self):
        return self.extra_views

    def wrap_extra_view(self, view_class):
        def wrapper(request, *args, **kwargs):
            viewkwargs = {}

            # There is no modelform_factory equivalent for plain forms.
            if issubclass(view_class, ModelFormMixin):
                # If the view_class doesn't have a model, set it with ours
                model = view_class.model or self.model
                form_class = view_class.form_class or forms.ModelForm

                # If the form_class defines the model, use that
                try:
                    model = form_class._meta.model or model
                except AttributeError:
                    # form_class is ModelForm, ModelForm doesn't have _meta
                    pass

                # Wrap the form class with the admin widgets
                Form = modelform_factory(
                    form=form_class,
                    model=model,
                    formfield_callback=partial(self.formfield_for_dbfield,
                                               request=request),
                )
                viewkwargs.update(
                    model=model,
                    form_class=Form,
                )

            viewfn = view_class.as_view(**viewkwargs)

            return viewfn(request, *args, **kwargs)
        return self.admin_site.admin_view(wrapper)

    def get_urls(self):
        from django.conf.urls import url
        my_urls = []

        for view_name, url_re, view_class in self.get_extra_views():
            url_name = '{app_label}_{model}_{view_name}'.format(
                app_label=self.model._meta.app_label,
                model=self.model._meta.model_name,
                view_name=view_name,
            )
            my_urls.append(
                url(url_re, self.wrap_extra_view(view_class), name=url_name),
            )

        return my_urls + super(ExtraViewsMixin, self).get_urls()
