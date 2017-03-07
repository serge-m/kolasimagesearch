from flask import Flask, request, jsonify

from image_processor import ImageProcessor
from impl.domain.source_image_metadata import EMPTY_METADATA

app = Flask(__name__)


@app.route('/api/search', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file_content = _get_file_content(request)
        search_result = ImageProcessor().process(file_content, EMPTY_METADATA)
        return jsonify(search_result)

    return '''Post image to this endpoint'''


def _get_file_content(flask_request):
    file_received = flask_request.files['file']
    file_content = file_received.read()
    return file_content


@app.route('/')
def root():
    return "Hello, World!"
