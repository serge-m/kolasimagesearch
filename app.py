from flask import Flask, request, jsonify

from image_processor import ImageProcessor
from impl.domain.source_image_metadata import SourceImageMetadata
import logging.config
from logging_config import logging_config

app = Flask(__name__)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

DUMMY_IMAGE_URL = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/Peloric_Streptocarpus_flower.jpg'


@app.route('/api/find_and_add', methods=['POST'])
def find_and_add():
    if request.method != 'POST':
        return {'message': 'Post image to this endpoint'}, 400

    file_content = _get_file_content(request)
    metadata = SourceImageMetadata(path=DUMMY_IMAGE_URL)
    search_results = ImageProcessor().find_and_add_by_image(file_content, metadata)
    result = jsonify({'success': True, 'data': search_results})
    return result, 200


@app.route('/api/find', methods=['POST'])
def find():
    if request.method != 'POST':
        return {'message': 'Post image to this endpoint'}, 400

    file_content = _get_file_content(request)
    search_results = ImageProcessor().find_by_image(file_content)
    result = jsonify({'success': True, 'data': search_results})
    return result, 200


@app.route('/api/add', methods=['POST'])
def add():
    json_data = request.get_json()

    if not json_data:
        return jsonify({'message': 'Unable to get URL from request. Request: {}'.format(json_data)}), 400
    try:
        url = json_data['url']
    except KeyError:
        return jsonify({'message': 'Unable to get url parameter from the request'}), 400

    try:
        ImageProcessor().add_by_url(url)
    except Exception as e:
        logger.exception('Failed to process image ')
        return jsonify({'message': 'image processing went wrong. {}'.format(e)}), 500

    return jsonify({'success': True}), 200


def _get_file_content(flask_request) -> bytes:
    file_received = flask_request.files['file']
    file_content = file_received.read()
    return file_content


@app.route('/')
def root():
    return "Hello, World!"


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': 'page not found'}), 404


if __name__ == "__main__":
    app.run()
