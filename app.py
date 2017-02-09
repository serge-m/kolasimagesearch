from flask import Flask, request, jsonify

from face_search.impl.source_image_metadata import SourceImageMetadata
from project.face_search.face_processor import FaceProcessor

app = Flask(__name__)


@app.route('/api/search', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file_content = _get_file_content(request)
        search_result = FaceProcessor().process(file_content, SourceImageMetadata())
        return jsonify(search_result)

    return '''Post image to this endpoint'''


def _get_file_content(flask_request):
    file_received = flask_request.files['file']
    file_content = file_received.read()
    return file_content


@app.route('/')
def root():
    return "Hello, World!"
