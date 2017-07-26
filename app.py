from flask import Flask, request, jsonify

from image_processor import ImageProcessor
from impl.domain.source_image_metadata import EMPTY_METADATA
import logging.config
from logging_config import logging_config

app = Flask(__name__)
logging.config.dictConfig(logging_config)


@app.route('/api/search', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file_content = _get_file_content(request)
        search_results = ImageProcessor().process(file_content, EMPTY_METADATA)
        return jsonify(search_results)

    return '''Post image to this endpoint'''


def _get_file_content(flask_request) -> bytes:
    file_received = flask_request.files['file']
    file_content = file_received.read()
    return file_content


@app.route('/')
def root():
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
