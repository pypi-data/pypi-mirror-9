from django.conf.urls import patterns, include, url
from models.news import News
from forms.news import NewsForm
from views.newsviewlet import NewsViewlet
from djinn_contenttypes.views.base import CreateView
from djinn_contenttypes.views.utils import generate_model_urls


_urlpatterns = patterns(
    "",

    url(r"^$",
        NewsViewlet.as_view(),
        name="djinn_news"),

    url(r"^add/article/(?P<parentusergroup>[\d]*)/$",
        CreateView.as_view(model=News, form_class=NewsForm,
                           fk_fields=["parentusergroup"]),
        name="djinn_news_add_news"),
    )

urlpatterns = patterns(
    '',
    (r'^news/', include(_urlpatterns)),
    (r'^news/', include(generate_model_urls(News))),
    )
