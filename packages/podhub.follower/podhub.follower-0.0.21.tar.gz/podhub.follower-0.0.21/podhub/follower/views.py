from . import app
from feed import Feed
from flask import jsonify, request


@app.route('/')
def index():
    return jsonify()


@app.route('/audio')
def feed():
    url = request.args.get('feed_url')
    index = request.args.get('index')
    if not index:
        index = -1

    feed = Feed(url=url)

    try:
        entry = feed.entries[index]
    except TypeError:
        return jsonify(error_message='index must be an integer.'), 400
    except IndexError:
        return jsonify(error_message='episode {} not found'.format(index)), 400

    return jsonify(feed_url=entry.audio)
