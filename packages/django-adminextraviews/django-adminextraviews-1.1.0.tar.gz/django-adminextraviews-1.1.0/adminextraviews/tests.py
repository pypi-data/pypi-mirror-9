import unittest

from django.test import TestCase
from django.conf.urls import url, include
from django.contrib import admin, auth
from django.core import urlresolvers
from django.views.generic import View, CreateView, FormView
from django.http import HttpResponse
from django import forms

from adminextraviews import ExtraViewsMixin


class HelloView(View):
    def get(self, request, name):
        return HttpResponse('hello ' + name)


class TextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)


class TextFormView(FormView):
    form_class = TextForm

    def render_to_response(self, context):
        return HttpResponse(context['form'].as_table())


class LogEntryCreateView(CreateView):
    def render_to_response(self, context):
        return HttpResponse(context['form'].as_table())


class DifferentModelView(CreateView):
    model = auth.models.User

    def render_to_response(self, context):
        return HttpResponse(context['form'].as_table())


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = auth.models.User


class DifferentModelView2(CreateView):
    form_class = UserAdminForm

    def render_to_response(self, context):
        return HttpResponse(context['form'].as_table())


class LogEntryAdmin(ExtraViewsMixin, admin.ModelAdmin):
    extra_views = [
        ('hello', r'^hello/(?P<name>\w+)/$', HelloView),
        ('form-view', r'^form-view$', TextFormView),
        ('my-create', r'^create/$', LogEntryCreateView),
        ('user-create', r'^user-create/$', DifferentModelView),
        ('user-create2', r'^user-create2/$', DifferentModelView2),
    ]


admin.site.register(admin.models.LogEntry, LogEntryAdmin)


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]


class AdminExtraViewsTestCase(TestCase):
    urls = 'adminextraviews.tests'

    def setUp(self):
        User = auth.get_user_model()
        self.user = User.objects.create_superuser('u', 'e@example.com', 'p')
        self.client.login(username='u', password='p')

    def test_url_reversing(self):
        url = urlresolvers.reverse('admin:admin_logentry_hello', kwargs={
            'name': 'foo',
        })
        self.assertEqual(url, '/admin/admin/logentry/hello/foo/')

    def test_hello_view(self):
        url = urlresolvers.reverse('admin:admin_logentry_hello', kwargs={
            'name': 'foo',
        })
        response = self.client.get(url)
        # The response.content is bytes in python 3
        self.assertEquals(response.content, b'hello foo')

    @unittest.expectedFailure
    def test_wraps_with_admin_widgets(self):
        url = urlresolvers.reverse('admin:admin_logentry_form-view')
        response = self.client.get(url)
        # vLargeTextField is a class that the admin widgets add
        self.assertContains(response, 'vLargeTextField')

    def test_plain_form_views_work(self):
        url = urlresolvers.reverse('admin:admin_logentry_form-view')
        response = self.client.get(url)
        # vLargeTextField is a class that the admin widgets add
        self.assertContains(response, 'id="id_text"')

    def test_set_model_automatically(self):
        url = urlresolvers.reverse('admin:admin_logentry_my-create')
        response = self.client.get(url)
        # object_id is a field that exists on LogEntry
        self.assertContains(response, 'object_id')
        # vLargeTextField is a class that the admin widgets add
        self.assertContains(response, 'vLargeTextField')

    def test_supports_different_models(self):
        url = urlresolvers.reverse('admin:admin_logentry_user-create')
        response = self.client.get(url)
        # LogEntry doesn't have a date_joined field
        self.assertContains(response, 'date_joined')

    def test_doesnt_overwrite_the_form_class_model(self):
        url = urlresolvers.reverse('admin:admin_logentry_user-create2')
        response = self.client.get(url)
        # LogEntry doesn't have a date_joined field
        self.assertContains(response, 'date_joined')
