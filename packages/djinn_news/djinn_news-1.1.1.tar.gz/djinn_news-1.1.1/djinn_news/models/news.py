from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.registry import CTRegistry
from djinn_contenttypes.models.publishable import PublishableContent
from djinn_contenttypes.models.attachment import ImgAttachment
from djinn_contenttypes.models.commentable import Commentable
from djinn_contenttypes.models.highlight import Highlight


class News(PublishableContent, Commentable):

    """ News content type """

    text = models.TextField(null=True, blank=True)

    images = models.ManyToManyField(ImgAttachment)

    show_images = models.BooleanField(default=True)

    is_global = models.BooleanField(default=False)

    create_tmp_object = True

    def documents(self):

        return self.get_related(relation_type="related_document")

    @property
    def date(self):

        return self.publish_from or self.created

    @property
    def human_date(self):

        delta = datetime.now() - self.date

        if delta.days == 0:
            return self.date.strftime('%H:%M')
        else:
            return self.date.strftime('%d-%m')

    @property
    def highlight_from(self):

        try:
            return Highlight.objects.get(
                object_id=self.id,
                object_ct__name="news").date_from
        except:
            return None

    class Meta:
        app_label = "djinn_news"


CTRegistry.register(
    "news",
    {"class": News,
     "app": "djinn_news",
     "group_add": True,
     "label": _("News")}
    )
