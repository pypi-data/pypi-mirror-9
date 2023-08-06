from django.conf.urls import url
from wagtailsettings import views


urlpatterns = [
    url(r'^(\w+)/(\w+)/$', views.edit, name='wagtailsettings_edit'),
]
