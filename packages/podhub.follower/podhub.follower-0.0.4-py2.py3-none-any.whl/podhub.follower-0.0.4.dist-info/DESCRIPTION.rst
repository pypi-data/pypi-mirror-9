# podhub.follower

HTTP service to find audio.

## Installation

Point your favorite wsgi server at `podhub.follower.app` otherwise install
`gevent` from PyPI and `libevent` from your favorite OS's package manager.

## Configuration

Add a config file at either `~/.config/podhub/follower/config.py` or
`/etc/podhub/follower/config.py`:

```
MEMCACHED_HOST = '127.0.0.1:11211'
URL_PARSE_TIMEOUT=86400  # 1 day
LOG_LEVEL = 'WARNING'
LOG_FILE = '/var/log/podhub/follower/app.log'
```

## API
* `/audio` [`GET`]: `feed_url` is the url to the podcast rss feed.
  `index` is the index representing the episode in the feed.


