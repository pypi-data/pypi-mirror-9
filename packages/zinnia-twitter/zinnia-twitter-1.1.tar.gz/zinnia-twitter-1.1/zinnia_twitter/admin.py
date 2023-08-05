"""EntryAdmin for zinnia-twitter"""
import tweepy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from zinnia.models import Entry
from zinnia.admin.entry import EntryAdmin
from zinnia.settings import ENTRY_BASE_MODEL

from zinnia_twitter import settings


class EntryAdminTwitterMixin(object):
    """
    Mixin adding action to post an update about an Entry
    on Twitter.
    """
    actions = ['make_tweet']

    def get_actions(self, request):
        """
        Unregister post update on Twitter action
        if required configuration is not set.
        """
        actions = super(EntryAdminTwitterMixin, self).get_actions(request)
        if not actions:
            return actions
        if not settings.USE_TWITTER:
            del actions['make_tweet']
        return actions

    def make_tweet(self, request, queryset):
        """
        Post an update on Twitter.
        """
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                   settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_KEY,
                              settings.TWITTER_ACCESS_SECRET)
        api = tweepy.API(auth)
        for entry in queryset:
            short_url = entry.short_url
            message = '%s %s' % (entry.title[:139 - len(short_url)], short_url)
            api.update_status(status=message)
        self.message_user(
            request, _('The selected entries have been tweeted.'))
    make_tweet.short_description = _('Tweet entries selected')


class EntryAdminTwitter(EntryAdminTwitterMixin,
                        EntryAdmin):
    """
    Enrich the default EntryAdmin with post on Twitter action.
    """
    pass


if ENTRY_BASE_MODEL == 'zinnia.models_bases.entry.AbstractEntry':
    admin.site.unregister(Entry)
    admin.site.register(Entry, EntryAdminTwitter)
