"""Django urls for contact form."""

from django.conf.urls import patterns, url

from contact_form.views import ContactFormView

urlpatterns = patterns('', url(r'^$', ContactFormView.as_view(), name='contact_form'), )
