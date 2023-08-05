from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from djinn_forms.widgets.attachment import AttachmentWidget
from djinn_forms.fields.relate import RelateField
from djinn_forms.forms.relate import RelateMixin
from djinn_forms.forms.richtext import RichTextMixin
from djinn_forms.widgets.relate import RelateWidget
from djinn_forms.widgets.richtext import RichTextWidget
from djinn_forms.widgets.datetimewidget import DateTimeWidget
from djinn_contenttypes.forms.base import BaseContentForm
from djinn_contenttypes.models.attachment import ImgAttachment
from djinn_contenttypes.models.highlight import Highlight
from djinn_news.models import News


class NewsForm(BaseContentForm, RelateMixin, RichTextMixin):

    # Translators: news general help
    help = _("Add a news item. The item will be submitted for publishing")

    title = forms.CharField(label=_("Title"),
                            max_length=100,
                            widget=forms.TextInput())

    text = forms.CharField(
        # Translators: news text label
        label=_("News text"),
        required=True,
        widget=RichTextWidget(
            img_type="djinn_contenttypes.ImgAttachment",
            attrs={'class': 'extended'}
        ))

    documents = RelateField(
        "related_document",
        ["pgcontent.document"],
        # Translators: news documents label
        label=_("Related documents"),
        required=False,
        # Translators: news documents help
        help_text=_("Select document(s)"),
        widget=RelateWidget(
            attrs={'hint': _("Search document"),
                   # Translators: djinn_news documents link label
                   'label': _("Search documents"),
                   'searchfield': 'title_auto',
                   'template_name':
                   'djinn_forms/snippets/relatesearchwidget.html',
                   'search_url': '/document_search/',
                   'ct_searchfield': 'meta_type', },
            )
        )

    images = forms.ModelMultipleChoiceField(
        queryset=ImgAttachment.objects.all(),
        # Translators: news images label
        label=_("Images"),
        required=False,
        widget=AttachmentWidget(
            ImgAttachment,
            "djinn_forms/snippets/imageattachmentwidget.html",
            attrs={"multiple": True}
            ))

    highlight_from = forms.DateTimeField(
        # Translators: contenttypes highlight_from label
        label=_("Highlight from"),
        # Translators: contenttypes publish_from help
        help_text=_("Enter a publish-from date and time"),
        required=False,
        widget=DateTimeWidget(
            attrs={'date_hint': _("Date"),
                   'time_hint': _("Time")}
            )
        )

    def __init__(self, *args, **kwargs):

        super(NewsForm, self).__init__(*args, **kwargs)

        self.fields['show_images'].label = _("Show images")
        self.fields['comments_enabled'].label = _("Comments enabled")

        if not self.user.has_perm("djinn_news.manage_news", obj=self.instance):
            del self.fields['highlight_from']
        else:
            self.fields[
                'highlight_from'].initial = self.instance.highlight_from

        self.init_relation_fields()
        self.init_richtext_widgets()

    def save(self, commit=True):

        object_ct = ContentType.objects.get_for_model(self.instance)

        if commit:
            if self.cleaned_data.get("highlight_from"):
                hlight, created = Highlight.objects.get_or_create(
                    object_id=self.instance.id,
                    object_ct=object_ct)

                hlight.date_from = self.cleaned_data.get("highlight_from")
                hlight.save()

                # del self.cleaned_data['highlight_from']
            else:
                Highlight.objects.filter(
                    object_id=self.instance.id,
                    object_ct=object_ct).delete()

        res = super(NewsForm, self).save(commit=commit)

        self.save_relations(commit=commit)

        return res

    class Meta(BaseContentForm.Meta):
        model = News
        fields = ('title', 'text', 'documents', 'images', 'parentusergroup',
                  'comments_enabled', 'owner', 'publish_from',
                  'remove_after_publish_to',
                  'publish_to', 'highlight_from', 'show_images')
