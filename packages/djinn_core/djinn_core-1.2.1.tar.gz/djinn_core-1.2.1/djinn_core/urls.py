from django.conf.urls import patterns, include, url
from views.admin import AdminView


_urlpatterns = patterns(
    "",

    url(r"^djinn_admin/?$",
        AdminView.as_view(),
        name="djinn_admin"),
)


urlpatterns = patterns(
    '',
    (r'^djinn/', include(_urlpatterns)),
    )
