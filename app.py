from flask import Flask, request, jsonify

from image_processor_facade import ImageProcessorFacade
from impl.domain.source_image_metadata import SourceImageMetadata
import logging.config
from logging_config import logging_config

app = Flask(__name__)
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

DUMMY_IMAGE_URL = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/Peloric_Streptocarpus_flower.jpg'


class WrongParametersError(Exception):
    pass


class ProcessingError(Exception):
    pass


@app.route('/api/find_and_add', methods=['POST'])
def find_and_add():
    if request.method != 'POST':
        return {'message': 'Post image to this endpoint'}, 400

    file_content = _get_file_content(request)
    metadata = SourceImageMetadata(path=DUMMY_IMAGE_URL)
    search_results = ImageProcessorFacade().find_and_add_by_image(file_content, metadata)
    result = jsonify({'success': True, 'data': search_results})
    return result, 200


@app.route('/api/find', methods=['POST'])
def find():
    if request.method != 'POST':
        return {'message': 'Post image to this endpoint'}, 400

    file_content = _get_file_content(request)
    search_results = ImageProcessorFacade().find_by_image(file_content)
    result = jsonify({'success': True, 'data': search_results})
    return result, 200


@app.route('/api/add_by_url', methods=['POST'])
def add_by_url():
    url = _get_url_from_request(request)
    try:
        ImageProcessorFacade().add_by_url(url)
    except Exception as e:
        logger.exception('Failed to process image ')
        raise ProcessingError('image processing went wrong. {}'.format(e)) from e

    return jsonify({'success': True}), 200


@app.route('/api/find_by_url', methods=['POST'])
def find_by_url():
    url = _get_url_from_request(request)
    try:
        search_results = ImageProcessorFacade().find_by_url(url)
    except Exception as e:
        logger.exception('Failed to process image ')
        raise ProcessingError('image processing went wrong. {}'.format(e)) from e

    result = jsonify({'success': True, 'data': search_results})
    return result, 200


def _get_url_from_request(request) -> str:
    json_data = request.get_json()

    if not json_data:
        raise Exception('Unable to get URL from request. Request: {}'.format(json_data))

    try:
        url = json_data['url']
    except KeyError as e:
        raise Exception('Unable to get url parameter from the request') from e
    logger.info('Decoded url "{}" from json request'.format(url))
    return url

def _get_file_content(flask_request) -> bytes:
    file_received = flask_request.files['file']
    file_content = file_received.read()
    return file_content


@app.route('/')
def root():
    return "Hello, World!"


@app.errorhandler(WrongParametersError)
def other_exceptions(e):
    return jsonify({'success': False, 'message': str(e)}), 400


@app.errorhandler(ProcessingError)
def other_exceptions(e):
    return jsonify({'success': False, 'message': str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': 'page not found'}), 404


if __name__ == "__main__":
    app.run()
