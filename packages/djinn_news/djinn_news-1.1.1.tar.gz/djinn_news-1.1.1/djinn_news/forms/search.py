from datetime import datetime
from djinn_search.forms.base import FixedFilterSearchForm


class HomepageNewsSearchForm(FixedFilterSearchForm):

    spelling_query = None

    def extra_filters(self, skip_filters=None):

        self.sqs = self.sqs.filter(homepage_published__lte=datetime.now())
