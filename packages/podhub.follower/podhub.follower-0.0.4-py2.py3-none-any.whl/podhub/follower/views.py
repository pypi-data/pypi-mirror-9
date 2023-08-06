import json
from . import app
from feed import Feed
from flask import jsonify, request


@app.route('/')
def index():
    return jsonify()


@app.route('/audio')
def feed():
    url = request.args.get('feed_url')
    if not url:
        return jsonify(error_message='feed_url required.')

    try:
        index = int(request.args.get('index'))
    except ValueError:
        err = 'index must be an integer.'
        app.logger.info(json.dumps({'user_error': err}))
        return jsonify(error_message=err), 400
    except TypeError:
        index = -1  # int(None) raises TypeError

    feed = Feed(url=url)
    app.logger.debug(json.dumps({'feed_title': feed.title}))

    try:
        entry = feed.entries[index]
        app.logger.debug(json.dumps({'entry_title': entry.title}))
    except IndexError:
        err = 'episode {} not found'.format(index)
        app.logger.info(json.dumps({'error': err}))
        return jsonify(error_message=err), 404

    app.logger.debug(json.dumps({'audio_url': entry.audio}))
    return jsonify(audio_url=entry.audio)
