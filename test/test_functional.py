import json
import os
from io import BytesIO
from typing import Dict
from unittest import mock

import pytest
from pytest import mark

from app import app, DUMMY_IMAGE_URL
from impl.domain.source_image_metadata import SourceImageMetadata
from kolasimagesearch.test.test_image_processor import expected_search_result

current_dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def client(request):
    test_client = app.test_client()

    def teardown():
        pass  # databases and resources have to be freed at the end. But so far we don't have anything

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
    return client.post(url, data=map_name_to_file_and_name, content_type='multipart/form-data', )


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def read_image(path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


class TestApp:
    image_data = read_image(os.path.join(current_dir_path, "test_data/test.jpg"))

    def test_dummy(self, client):
        response = client.get('/')
        assert b'Hello, World!' in response.data

    @mark.skip()
    def test_post_find_and_add_by_image(self, client):
        response = post_files(client, '/api/find_and_add', {'file': BytesIO(self.image_data)})
        assert "normalized image is saved in image storage"
        assert "source image metadata is saved in descriptor storage"
        assert "descriptors are calculated for for normalized image and stored in the descriptor storage"
        assert "similar image are returned to user"
        assert response.status_code == 200

    @mock.patch('app.ImageProcessorFacade', spec=True)
    def test_post_find_and_add_by_image_mocked(self, img_processor_facade, client):
        img_processor_facade.return_value.find_and_add_by_image.return_value = expected_search_result

        response = post_files(client, '/api/find_and_add', {'file': BytesIO(self.image_data)})

        img_processor_facade.assert_called_once_with()
        img_processor_facade.return_value.find_and_add_by_image.assert_called_once_with(
            self.image_data, SourceImageMetadata(DUMMY_IMAGE_URL)
        )
        assert response.status_code == 200
        assert json_of_response(response) == {"data": expected_search_result,
                                              "success": True}
