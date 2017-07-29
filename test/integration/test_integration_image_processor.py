import shutil

import pytest
import tempfile
from io import BytesIO
from typing import List
from unittest import mock

import numpy as np
from PIL import Image

from image_processor import ImageProcessor
from impl.domain.source_image_metadata import EMPTY_METADATA

# noinspection PyUnresolvedReferences
from impl.test.elastic_fixtures import unique_temp_index, another_unique_temp_index, index_name

from kolasimagestorage.image_encoder import ImageEncoder


def _combine(image1, image2):
    return np.hstack([image1, image2])


_format = "jpeg"

block_size = 16

pos1 = [0, 0]
pos2 = [block_size, 0]
pos3 = [block_size, block_size]

positions = [pos1, pos2, pos3]


def numpy_to_binary(image: np.ndarray) -> bytes:
    im = Image.fromarray(np.uint8(image))
    file_like = BytesIO()
    im.save(file_like, format=_format)
    return file_like.getvalue()


def _put_color_square(color, img, pos):
    y, x = pos
    img[y:y + block_size, x:x + block_size] = color


def _generate_subimage(list_positions: List, list_colors: List):
    img = np.zeros([h, w, num_channels], dtype='uint8')

    for color, position in zip(list_colors, list_positions):
        _put_color_square(color, img, position)

    return img


@pytest.fixture
def temp_location_for_storage():
    tmp_storage_location = tempfile.mkdtemp()
    yield tmp_storage_location
    shutil.rmtree(tmp_storage_location)


h = 32
w = 64
num_channels = 3

rs = np.random.RandomState(0)

color1 = [255, 255, 255]
color2 = [128, 128, 128]
color3 = [64, 64, 64]
color4 = [32, 32, 32]
raw1 = _combine(_generate_subimage(list_positions=positions, list_colors=[color1, color2, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color2, color1, color3]))

raw2 = _combine(_generate_subimage(list_positions=positions, list_colors=[color3, color2, color1]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color3, color4]))

raw3 = _combine(_generate_subimage(list_positions=positions, list_colors=[color4, color3, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color3, color4]))

raw4 = _combine(_generate_subimage(list_positions=positions, list_colors=[color2, color2, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color4, color4]))

raw_images = [raw1, raw2, raw3, raw4]
images = [numpy_to_binary(raw) for raw in raw_images]


class TestIntegrationImageProcessor:
    def test_codec_preserves_images_to_make_results_reproducible(self):
        encoder = ImageEncoder(image_format="jpeg")
        for raw, image in zip(raw_images, images):
            decoded = encoder.binary_to_array(image)
            assert np.array_equal(raw, decoded)

    @mock.patch('impl.storage.source_image_storage.config')
    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.search_words.search_terms_creator.config_descriptors')
    def test_integration_image_processor(self, c3, c2, c, unique_temp_index, another_unique_temp_index, temp_location_for_storage):
        c.ELASTIC_SOURCE_IMAGES_INDEX = unique_temp_index
        c.ELASTIC_SOURCE_IMAGES_TYPE = "images_" + unique_temp_index
        c.FILE_SERVICE_PARAMETERS = {
            "driver_name": "local",
            "storage_driver_parameters": {
                "key": temp_location_for_storage,
            },
            "container_name": "container",
        }
        c2.ELASTIC_DESCRIPTOR_INDEX = another_unique_temp_index
        c2.ELASTIC_DESCRIPTOR_TYPE = "descriptors_" + another_unique_temp_index
        c3.LENGTH_OF_WORD = 2
        c3.NUMBER_OF_LEVELS = 4
        c3.DESCRIPTOR_LENGTH = 16*3

        processor = ImageProcessor(flush_data=True)
        res1 = processor.process(images[0], EMPTY_METADATA)
        assert res1[0] == []
        assert len(res1[1]) == 1  # region from first half of the image is found
        assert res1[1][0]["distance"] == 0

        res2 = processor.process(images[1], EMPTY_METADATA)
        similar2_0 = res2[0]
        similar2_1 = res2[1]
        assert len(similar2_0) == 1  # one is found
        assert similar2_0[0]["distance"] == 0  # descriptors are equivalent
        assert len(similar2_1) == 1
        assert similar2_1[0]["distance"] == 3.0  # descriptors are different equivalent

        res3 = processor.process(images[0], EMPTY_METADATA)
        res4 = processor.process(images[2], EMPTY_METADATA)
