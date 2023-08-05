from urllib import unquote_plus
from django import forms
from django.utils.translation import ugettext_lazy as _
from markupfield.widgets import MarkupTextarea
from djinn_contenttypes.forms.base import BaseSharingForm
from djinn_forms.widgets.link import LinkWidget
from djinn_contenttypes.forms.fields import NoScriptCharField
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from djinn_announcements.settings import SERVICEANNOUNCEMENT_STATUS_VOCAB, \
    ANNOUNCEMENT_PRIORITY_VOCAB


class ServiceAnnouncementForm(BaseSharingForm):

    # Translators: serviceannouncement edit general help
    help = _("Edit serviceannouncement")

    text = NoScriptCharField(
        # Translators: serviceannouncement edit text label
        label=_("Description"),
        help_text="Maximaal 500 karakters",
        max_length=500,
        widget=MarkupTextarea(
            attrs={'class': 'full count_characters',
                   'data-maxchars': '500'}
        ))

    start_date = forms.DateTimeField(
        # Translators: serviceannouncement edit start_date label
        label=_("Start date"),
        widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
        )
    )

    end_date = forms.DateTimeField(
        # Translators: serviceannouncement edit end_date label
        label=_("(Expected) end date"),
        required=False,
        widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
            )
        )

    remove_after_publish_to = forms.BooleanField(
        # Translators: news remove_after_end label
        label=_("Remove after end date"),
        required=False
        )

    status = forms.IntegerField(
        # Translators: serviceannouncement edit status label
        label=_("Status"),
        required=False,
        initial=-1,
        widget=forms.Select(
            choices=SERVICEANNOUNCEMENT_STATUS_VOCAB)
        )

    priority = forms.IntegerField(
        # Translators: serviceannouncement edit priority label
        label=_("Priority"),
        initial=0,
        widget=forms.Select(
            choices=ANNOUNCEMENT_PRIORITY_VOCAB)
        )

    link = forms.CharField(
        # Translators: serviceannouncement edit link label
        label=_("Link"),
        required=False,
        max_length=200,
        widget=LinkWidget())

    def clean_link(self):

        """ Always store the unquoted version """

        return unquote_plus(self.cleaned_data['link'])

    def __init__(self, *args, **kwargs):

        super(ServiceAnnouncementForm, self).__init__(*args, **kwargs)

        self.fields['title'].max_length = 100

        self.init_relation_fields()
        self.init_share_fields()
        self.fields['owner'].initial = kwargs['user'].profile

    def save(self, commit=True):

        res = super(ServiceAnnouncementForm, self).save(commit=commit)

        self.save_relations(commit=commit)
        self.save_shares(commit=commit)

        return res

    class Meta(BaseSharingForm.Meta):
        model = ServiceAnnouncement
