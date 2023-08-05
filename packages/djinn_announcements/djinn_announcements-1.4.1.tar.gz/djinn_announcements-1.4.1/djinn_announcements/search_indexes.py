from haystack import indexes
from djinn_announcements.models.announcement import Announcement
from djinn_announcements.models.serviceannouncement import ServiceAnnouncement
from pgsearch.base import ContentSearchIndex


class ServiceAnnouncementIndex(ContentSearchIndex, indexes.Indexable):

    def index_queryset(self, using=None):

        return self.get_model()._default_manager.all()

    def get_model(self):

        return ServiceAnnouncement

