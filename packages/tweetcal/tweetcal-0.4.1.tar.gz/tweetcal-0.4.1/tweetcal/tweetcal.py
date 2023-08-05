#!/usr/bin/env python
# encoding: utf-8
# Copyright (c) 2014 Neil Freeman

from os import path
from icalendar import Calendar, Event
import twitter_bot_utils as tbu
from HTMLParser import HTMLParser
import pytz
from datetime import timedelta
import tweepy
import logging


def setup_logger(verbose=None):
    logger = logging.getLogger('tweetcal')

    if verbose:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('tweetcal: %(message)s'))
        logger.addHandler(ch)

    return logger


def get_settings_and_keys(args):
    setup_logger(args.verbose or args.dry_run)

    argsdict = dict((k, v) for k, v in list(vars(args).items()) if v is not None)

    settings, keys = tbu.confighelper.configure(args.user, args.config, **argsdict)

    settings['file'] = path.join(path.dirname(__file__), settings['file'])

    return settings, keys


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=1)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        # Add link to tweet.
        url = u'http://twitter.com/{0}/status/{1}'.format(tweet.user.screen_name, tweet.id_str)
        event.add('url', url)

        # Add tweet's text.
        text = tbu.helpers.replace_urls(tweet)
        text = HTMLParser().unescape(text)
        event.add('summary', text)

        # Add tweet's date.
        dtstart, dtend = parse_date(tweet.created_at)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)

        # Add UID and special field for ID.
        event.add('uid', u'{0}@{1}.twitter'.format(tweet.id_str, tweet.user.screen_name))
        event['X-TWEET-ID'] = tweet.id_str

    except Exception as e:
        logger = logging.getLogger('tweetcal')
        logger.error(e)
        logger.error(u"{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))

    else:
        return event


def get_calendar(filename):
    '''Open calendar file and return as Calendar object, along with list of IDs retrieved (to avoid dupes)'''
    with open(filename, 'rb') as h:
        contents = h.read()
        logging.getLogger('tweetcal').info("Opened calendar file " + filename)

    if contents == '':
        raise IOError("Empty Calendar")

    return Calendar.from_ical(contents)


def new_calendar(user=None):
    if user:
        name = user + ' tweets'
    else:
        name = 'Tweets'

    cal = Calendar()
    cal.add('PRODID', '-//tweetcal//twitter importer//EN')
    cal.add('X-WR-CALNAME', name)
    return cal


def get_since_id(cal, since_id=None):
    '''Set the max and since ids to request from twitter. If the calendar has a max ID, use it as the since'''

    since_id = since_id or cal.get('X-MAX-TWEET-ID', None)
    logging.getLogger('tweetcal').debug('Setting since_id: {}'.format(str(since_id)))

    if since_id:
        return {'since_id': since_id}
    else:
        return {}

def set_max_id(cal, ids):
    '''Combine set of read IDs and just-added IDs to get the new max id'''
    try:
        max_id = max(ids)

    # If that's empty, there will be a ValueError, which is fine.
    except ValueError:
        max_id = 0

    cal['X-MAX-TWEET-ID'] = max(cal.get('X-MAX-TWEET-ID', 100000), max_id)

    logging.getLogger('tweetcal').debug('Set {1} to {0}'.format(max_id, 'X-MAX-TWEET-ID'))


def set_color(cal, status):
    if hasattr(status, 'user') and hasattr(status.user, 'profile_link_color'):
        cal['X-APPLE-CALENDAR-COLOR'] = '#' + status.user.profile_link_color


def get_tweets(consumer_key, consumer_secret, key, secret, **kwargs):
    # Auth and check twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)

    logging.getLogger('tweetcal').debug(
        "Setting up connection to Twitter API (since_id: {})".format(kwargs.get('since_id')))

    return tweepy.Cursor(api.user_timeline, **kwargs)


def add_to_calendar(cal, generator):
    """Add tweets to the calendar object"""
    ids, status = (), None

    # Loop the cursors and create the events if the tweet doesn't yet exist
    for status in generator():
        event = create_event(status)
        cal.add_component(event)

        try:
            ids = ids + (status.id, )
        except AttributeError:
            ids = ids + (int(status.id_str), )

    logging.getLogger('tweetcal').info('Inserted {} tweets.'.format(len(ids)))

    set_color(cal, status)
    set_max_id(cal, ids)


def write_calendar(cal, calendar_file):
    ical = cal.to_ical()
    open(path.expanduser(calendar_file), 'wb').write(ical)


def tweetcal(args):
    logger = logging.getLogger('tweetcal')

    try:
        settings, keys = get_settings_and_keys(args)

    except IOError as e:
        print(e)
        exit()

    if len(keys) != 4:
        raise ValueError("Incomplete settings: Don't have complete keys for @" + settings['user'])

    try:
        cal = get_calendar(settings['file'])

    except IOError:
        cal = new_calendar(settings['user'])

    since = get_since_id(cal, settings.get('since_id'))

    cursor = get_tweets(
        consumer_key=keys['consumer_key'],
        consumer_secret=keys['consumer_secret'],
        key=keys['key'],
        secret=keys['secret'],
        **since
    )

    logger.info("Grabbing tweets for @" + settings['user'])

    try:
        add_to_calendar(cal, cursor.items)

    except tweepy.error.TweepError as e:
        print(e.message)
        exit(-1)

    if settings['dry_run']:
        logger.info('Ending without rewriting file.')

    else:
        logger.info('Writing tweets to file.')
        write_calendar(cal, settings['file'])
