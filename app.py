from flask import Flask, request, jsonify

from image_processor import ImageProcessor
from impl.domain.source_image_metadata import EMPTY_METADATA, SourceImageMetadata
import logging.config
from logging_config import logging_config

app = Flask(__name__)
logging.config.dictConfig(logging_config)


@app.route('/api/search', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file_content = _get_file_content(request)
        metadata = SourceImageMetadata(path='https://upload.wikimedia.org/wikipedia/commons/a/ac/Peloric_Streptocarpus_flower.jpg')
        search_results = ImageProcessor().process(file_content, metadata)
        result = jsonify({'success': True, 'data': search_results})
        print(result)
        return result, 200

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
