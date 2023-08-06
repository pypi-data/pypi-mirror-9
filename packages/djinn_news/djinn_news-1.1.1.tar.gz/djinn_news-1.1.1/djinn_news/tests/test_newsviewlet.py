from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from djinn_news.models.news import News
from djinn_news.views.newsviewlet import NewsViewlet
from djinn_contenttypes.models.highlight import Highlight


class NewsViewletTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()
        self.user = get_user_model().objects.create(username="bobdobalina")

    def test_news(self):

        news0 = News.objects.create(
            title="Now this is news!",
            changed_by=self.user,
            creator=self.user)

        request = self.factory.get('/news/')
        request.user = self.user

        response = NewsViewlet.as_view()(request)

        view = response.context_data['view']

        self.assertEqual(0, len(view.news()))

        hl = Highlight.objects.create(content_object=news0)

        self.assertEqual(1, len(view.news()))

        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        hl.date_from = tomorrow
        hl.save()

        self.assertEqual(0, len(view.news()))

        hl.date_from = yesterday
        hl.save()

        self.assertEqual(1, len(view.news()))

        news0.publish_to = yesterday
        news0.save()

        self.assertEqual(0, len(view.news()))

        news0.publish_to = tomorrow
        news0.save()

        self.assertEqual(1, len(view.news()))
