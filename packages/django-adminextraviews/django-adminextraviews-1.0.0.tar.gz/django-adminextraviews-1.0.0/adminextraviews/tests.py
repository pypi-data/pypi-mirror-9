from django.test import TestCase
from django.conf.urls import url, include
from django.contrib import admin, auth
from django.core import urlresolvers
from django.views.generic import View, CreateView
from django.http import HttpResponse

from adminextraviews import ExtraViewsMixin


class HelloView(View):
    def get(self, request, name):
        return HttpResponse('hello ' + name)


class LogEntryCreateView(CreateView):
    def render_to_response(self, context):
        return HttpResponse(context['form'].as_table())


class LogEntryAdmin(ExtraViewsMixin, admin.ModelAdmin):
    extra_views = [
        ('hello', r'^hello/(?P<name>\w+)/$', HelloView),
        ('my-create', r'^create/$', LogEntryCreateView),
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

    def test_create_view(self):
        url = urlresolvers.reverse('admin:admin_logentry_my-create')
        response = self.client.get(url)
        # vLargeTextField is a class that the admin widgets add
        self.assertContains(response, 'vLargeTextField')
