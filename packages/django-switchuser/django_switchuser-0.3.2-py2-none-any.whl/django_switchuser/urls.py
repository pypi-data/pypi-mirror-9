from django.conf.urls.defaults import patterns, url

from . import views

urlpatterns = patterns("",
    url(r"^$", views.su_login, name="su-login"),
    url(r"^logout$", views.su_logout, name="su-logout"),
)
