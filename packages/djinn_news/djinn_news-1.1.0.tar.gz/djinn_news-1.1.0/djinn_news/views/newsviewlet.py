from django.views.generic import TemplateView
from django.conf import settings
from djinn_contenttypes.views.base import AcceptMixin
from djinn_contenttypes.models.highlight import Highlight
from djinn_news.models.news import News
from datetime import datetime
from django.db.models.query import Q


SHOW_N = getattr(settings, "DJINN_SHOW_N_NEWS_ITEMS", 5)


class NewsViewlet(AcceptMixin, TemplateView):

    template_name = "djinn_news/snippets/news_viewlet.html"

    news_list = None
    has_more = False

    def news(self, limit=SHOW_N):

        now = datetime.now()

        if not self.news_list:

            highlighted = Highlight.objects.filter(
                object_ct__name="news"
            ).filter(
                Q(date_from__isnull=True) | Q(date_from__lte=now)
            ).filter(
                Q(date_to__isnull=True) | Q(date_to__gte=now)
            ).order_by("-date_from")

            self.news_list = []
            for hl in highlighted:
                news = hl.content_object
                if (not news.publish_from or news.publish_from <= now) and \
                        (not news.publish_to or news.publish_to > now) and \
                        news.title:
                    self.news_list.append(hl)
                    if len(self.news_list) == limit:
                        self.has_more = True
                        break
        return self.news_list


    @property
    def show_more(self, limit=SHOW_N):
        if not self.news_list:
            self.news(limit=limit)
        return self.has_more
