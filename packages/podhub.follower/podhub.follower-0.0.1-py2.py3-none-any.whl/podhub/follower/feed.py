from . import app, mc
from hashlib import md5
import feedparser
import uuid


class Feed(object):

    _PARAMS = frozenset([
        'author', 'author_detail', 'authors', 'generator', 'generator_detail',
        'image', 'itunes_explicit', 'language', 'link', 'links', 'publisher',
        'publisher_detail', 'rawvoice_frequency', 'rawvoice_rating', 'rights',
        'rights_detail', 'subtitle', 'subtitle_detail', 'summary',
        'summary_detail', 'sy_updatefrequency', 'sy_updateperiod', 'tags',
        'title', 'title_detail', 'updated', 'updated_parsed'
    ])

    def __init__(self, url=None, **kwargs):
        self.url = url
        if url is not None:
            self.parse_feed()
        self.lookup = {entry.entry_id: entry for entry in self.entries}

    def parse_feed(self):
        url_hash = md5(self.url).hexdigest()

        d = mc.get(url_hash)
        if not d:
            d = feedparser.parse(self.url)
            mc.set('/parsed_url/{}'.format(url_hash), d,
                   time=app.config.get('URL_PARSE_TIMEOUT'))

        feed_obj = d.feed
        for key in self._PARAMS:
            setattr(self, key, feed_obj.feed.pop(key))
        self._custom_keys = feed_obj.feed

        _feed_hash = md5(''.join([self.url, self.title])).hexdigest()
        self.feed_id = mc.get('/feeds/{}'.format(_feed_hash))
        if not self.feed_id:
            self.feed_id = uuid.uuid4()
            mc.set('/feeds/{}'.format(_feed_hash), self.feed_id)

        self.entries = frozenset(Entry(**dict({'feed_id': self.feed_id}, **entry)) for entry in d.entries)  # noqa


class Entry(object):

    _PARAMS = frozenset([
        'author', 'author_detail', 'authors', 'comments', 'content', 'feed_id',
        'guidislink', 'id', 'itunes_duration', 'itunes_explicit', 'link',
        'links', 'published', 'published_parsed', 'slash_comments', 'subtitle',
        'subtitle_detail', 'summary', 'summary_detail', 'tags', 'title',
        'title_detail', 'wfw_commentrss'
    ])

    def __init__(self, **kwargs):
        for key in self._PARAMS:
            setattr(self, key, kwargs.get(key))

        self.entry_id = md5(self.id).hexdigest()

    @property
    def audio(self):
        """
        :return href: URL of audio file for podcast.
        :rtype  href: ``str``
        """
        mc_path = '/audio/{}/{}'.format(self.feed_id, self.entry_id)
        audio_link = mc.get(mc_path)
        if audio_link:
            return audio_link
        else:
            audio_link = filter(
                lambda x: x.get('rel') == 'enclosure', self.links).next().get(
                    'href')
            mc.set(mc_path, audio_link)
            return audio_link
