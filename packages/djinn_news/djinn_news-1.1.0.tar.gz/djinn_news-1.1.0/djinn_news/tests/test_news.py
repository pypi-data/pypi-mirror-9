from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from djinn_news.models.news import News
from djinn_contenttypes.models.highlight import Highlight


class NewsTest(TestCase):

    def setUp(self):

        self.user = get_user_model().objects.create(username="bobdobalina")

    def test_highlight_from(self):

        news0 = News.objects.create(
            title="Now this is news!",
            changed_by=self.user,
            creator=self.user)

        self.assertTrue(news0.highlight_from is None)

        hl = Highlight.objects.create(content_object=news0)

        self.assertTrue(news0.highlight_from is None)

        now = datetime.now()

        hl.date_from = now
        hl.save()

        self.assertEquals(now, news0.highlight_from)

    def test_post_delete(self):

        news0 = News.objects.create(
            title="Now this is news!",
            changed_by=self.user,
            creator=self.user)

        Highlight.objects.create(content_object=news0)

        self.assertEquals(1, Highlight.objects.all().count())

        news0.delete()

        self.assertEquals(0, Highlight.objects.all().count())
