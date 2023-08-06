from djinn_news.models.news import News
from haystack import indexes
from pgsearch.base import ContentSearchIndex
from datetime import datetime

class NewsIndex(ContentSearchIndex, indexes.Indexable):

    published = indexes.DateTimeField(model_attr='publish_from', null=True)

    homepage_published = indexes.DateTimeField(null=True)

    def prepare_homepage_published(self, obj):
        return obj.highlight_from

    def prepare_published(self, obj):
        return obj.date

    def get_model(self):

        return News
