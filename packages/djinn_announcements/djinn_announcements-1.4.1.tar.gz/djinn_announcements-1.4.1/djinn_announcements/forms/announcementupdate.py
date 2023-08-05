from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import removetags
from markupfield.widgets import MarkupTextarea
from djinn_contenttypes.forms.base import PartialUpdateMixin
from djinn_announcements.models.announcementupdate import AnnouncementUpdate


class AnnouncementUpdateForm(PartialUpdateMixin, forms.ModelForm):

    date = forms.DateTimeField(
        label=_("Date"),
        widget=forms.DateTimeInput(
            attrs={'class': 'datetime'},
            format="%d-%m-%Y %H:%M"
        ))

    text = forms.CharField(
        label=_("Description"),
        max_length=500,
        help_text="Maximaal 500 karakters",
        widget=MarkupTextarea(
            attrs={'class': 'full count_characters',
                   'data-maxchars': '500'}
        ))

    @property
    def labels(self):

        return {'submit': 'Opslaan', 'cancel': 'Annuleren'}

    def clean_text(self):

        value = self.cleaned_data['text'] or ""

        return removetags(value, 'script')

    class Meta:
        model = AnnouncementUpdate
        widgets = {'announcement': forms.HiddenInput()}
