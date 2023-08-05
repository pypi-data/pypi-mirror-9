from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.contrib.auth.models import Permission
from django.conf import settings
from pgauth.models import Role
from pgauth.settings import USER_ROLE_ID, OWNER_ROLE_ID, ADMIN_ROLE_ID, \
    EDITOR_ROLE_ID
from pgevents.register_events import base_event
from pgevents.events import Events
from djinn_news import models


def create_permissions(**kwargs):

    contenttype = ContentType.objects.get(
        app_label='djinn_news',
        model='news')

    role_user = Role.objects.get(name=USER_ROLE_ID)
    role_owner = Role.objects.get(name=OWNER_ROLE_ID)
    role_admin = Role.objects.get(name=ADMIN_ROLE_ID)
    role_editor = Role.objects.get(name=EDITOR_ROLE_ID)

    add, created = Permission.objects.get_or_create(
        codename="add_news",
        content_type=contenttype,
        defaults={'name': 'Add news'})

    manage, created = Permission.objects.get_or_create(
        codename="manage_news",
        content_type=contenttype,
        defaults={'name': 'Manage news'})

    edit, created = Permission.objects.get_or_create(
        codename="change_news",
        content_type=contenttype,
        defaults={'name': 'Change news'})

    delete, created = Permission.objects.get_or_create(
        codename="delete_news",
        content_type=contenttype,
        defaults={'name': 'Delete news'})

    role_user.add_permission_if_missing(add)
    role_owner.add_permission_if_missing(edit)
    role_editor.add_permission_if_missing(edit)
    role_owner.add_permission_if_missing(delete)
    role_admin.add_permission_if_missing(manage)


def register_events(**kwargs):

    def new_news(**kwargs):
        base_event("new_news", notify=False, **kwargs)

    def delete_news(**kwargs):
        base_event("delete_news", notify=False, **kwargs)

    Events.register("new_news", new_news)
    Events.register("delete_news", delete_news)


def set_default_settings(**kwargs):

    settings.configure(SHOW_N_NEWS_ITEMS=5)


signals.post_syncdb.connect(create_permissions, sender=models)
signals.post_syncdb.connect(register_events, sender=models)
#signals.post_syncdb.connect(set_default_settings, sender=models)
