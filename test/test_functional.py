import json
from io import BytesIO
from typing import Dict

import pytest
from face_search.app import app


@pytest.fixture
def client(request):
    test_client = app.test_client()

    def teardown():
        pass  # databases and resourses have to be freed at the end. But so far we don't have anything

    request.addfinalizer(teardown)
    return test_client


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')


def post_files(client, url, map_name_to_file: Dict):
    """Posts Multipart-encoded files to url
    :param client: flask test client fixture
    :param url: string URL
    :param map_name_to_file: dictionary name->file-like object
    """

    map_name_to_file_and_name = {name: (file, "mocked_name_{}".format(name)) for
                                 name, file in map_name_to_file.items()}
    return client.post(url, data=map_name_to_file_and_name, content_type='multipart/form-data',)


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def read_image(path):
    with open(path, "rb") as f:
        return BytesIO(f.read())


class TestApp:
    image_file = read_image("./test_data/test.jpg")

    def test_dummy(self, client):
        response = client.get('/')
        assert b'Hello, World!' in response.data

    def test_post_search(self, client):
        response = post_files(client, '/api/search', {'file': self.image_file})
        assert response.status_code == 200



