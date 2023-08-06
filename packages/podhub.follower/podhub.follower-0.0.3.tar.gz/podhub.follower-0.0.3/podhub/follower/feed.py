from . import app, mc
from hashlib import md5
import feedparser
import json
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
        app.logger.debug(json.dumps({'url': self.url}))
        if url is not None:
            self.parse_feed()
        self.lookup = {entry.entry_id: entry for entry in self.entries}

    def parse_feed(self):
        url_hash = md5(self.url).hexdigest()
        app.logger.info(json.dumps({'url': self.url, 'url_hash': url_hash}))

        d = mc.get(url_hash)
        if d:
            app.logger.debug(
                json.dumps({'msg': 'Feed title {} parsed.'.format(d.title),
                            'from_cache': True}))
        else:
            d = feedparser.parse(self.url)
            app.logger.debug(
                json.dumps({'msg': 'Feed title {} parsed.'.format(d.title),
                            'from_cache': False}))
            mc.set('/parsed_url/{}'.format(url_hash), d,
                   time=app.config.get('URL_PARSE_TIMEOUT'))

        feed_obj = d.feed
        for key in self._PARAMS:
            setattr(self, key, feed_obj.get(key))
        self._custom_keys = feed_obj

        _feed_hash = md5(''.join([self.url, self.title])).hexdigest()
        app.logger.info(json.dumps({'feed_hash': _feed_hash}))
        self.feed_id = mc.get('/feeds/{}'.format(_feed_hash))
        if self.feed_id:
            app.logger.info(json.dumps({'feed_id': self.feed_id,
                                        'from_cache': True}))
        else:
            self.feed_id = uuid.uuid4()
            app.logger.info(json.dumps({'feed_id': self.feed_id,
                                        'from_cache': False}))
            mc.set('/feeds/{}'.format(_feed_hash), self.feed_id)

        self.entries = tuple(Entry(**dict({'feed_id': self.feed_id}, **entry)) for entry in d.entries)  # noqa
        app.logger.debug(json.dumps({'entries_in_feed': len(self.entries)}))



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
            app.logger.debug(json.dumps({'audio_link': audio_link,
                                         'from_cache': True}))
            return audio_link
        else:
            audio_link = filter(
                lambda x: x.get('rel') == 'enclosure', self.links)[0].get(
                    'href')
            mc.set(mc_path, audio_link)
            app.logger.debug(json.dumps({'audio_link': audio_link,
                                         'from_cache': False}))
            return audio_link
