"""
Command for getting the Twitter oauth access.

http://talkfast.org/2010/05/31/twitter-from-the-command-line-in-python-using-oauth/
"""
from django.core.management.base import NoArgsCommand

import tweepy


class Command(NoArgsCommand):
    """
    This is an implementation of script showed in the
    step 3 of the tutorial.
    """
    help = 'Get access to your Twitter account'

    def handle_noargs(self, **options):
        CONSUMER_KEY = raw_input('Paste your Consumer Key here: ')
        CONSUMER_SECRET = raw_input('Paste your Consumer Secret here: ')

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.secure = True
        auth_url = auth.get_authorization_url()
        print 'Please authorize: ' + auth_url

        verifier = raw_input('PIN: ').strip()
        auth.get_access_token(verifier)

        print("ACCESS_KEY = '%s'" % auth.access_token.key)
        print("ACCESS_SECRET = '%s'" % auth.access_token.secret)
