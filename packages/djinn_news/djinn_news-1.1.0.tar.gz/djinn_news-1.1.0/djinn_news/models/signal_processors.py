from django.db.models.signals import post_delete
from django.dispatch import receiver
from djinn_news.models.news import News
from djinn_contenttypes.models.highlight import Highlight


@receiver(post_delete, sender=News)
def product_post_delete(sender, instance, **kwargs):

    Highlight.objects.filter(
        object_id=instance.id,
        object_ct__name="news").delete()
