# podhub.follower

HTTP service to find audio.

## Installation

Point your favorite wsgi server at `podhub.follower.app` otherwise install
`gevent` from PyPI and `libevent` from your favorite OS's package manager.

## API
* `/audio` [`GET`]: `feed_url` is the url to the podcast rss feed.
  `index` is the index representing the episode in the feed.


