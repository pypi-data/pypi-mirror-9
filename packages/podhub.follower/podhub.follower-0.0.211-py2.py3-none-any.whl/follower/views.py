from app import app
from feed import Entry, Feed
from flask import jsonify

@app.route('/')
def index():
    return jsonify()

@app.route('/cast/<url>/<index>')
def feed(url, index):
    """
    :param url: Podcast feed URL.
    :type  url: ``str``

    :param index: Index representing the episode number, defaults to latest.
    :type  index: ``int``
    """
    feed = Feed(url=url)

    try:
        entry = feed.lookup.get(index)
    except TypeError:
        return jsonify(error_message='index must be an integer.'), 400
    except IndexError:
        return jsonify(error_message='episode {} not found'.format(index)), 400

    return jsonify(feed_url=entry.audio)
