import shutil

import pytest
import tempfile
from io import BytesIO
from typing import List
from unittest import mock

import numpy as np
from PIL import Image

from image_processor_facade import ImageProcessorFacade
from impl.domain.source_image_metadata import SourceImageMetadata

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
raw0 = _combine(_generate_subimage(list_positions=positions, list_colors=[color1, color2, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color2, color1, color3]))

raw1 = _combine(_generate_subimage(list_positions=positions, list_colors=[color3, color2, color1]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color3, color4]))

raw2 = _combine(_generate_subimage(list_positions=positions, list_colors=[color4, color3, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color3, color4]))

raw3 = _combine(_generate_subimage(list_positions=positions, list_colors=[color2, color2, color3]),
                _generate_subimage(list_positions=positions, list_colors=[color3, color4, color4]))

raw_images = [raw0, raw1, raw2, raw3]
images = [numpy_to_binary(raw) for raw in raw_images]


def found_result(distance_3, saved_source_id, url):
    return {'metadata': {'url': url}, 'source_id': saved_source_id, 'distance': distance_3}


class TestIntegrationImageProcessor:
    def test_codec_preserves_images_to_make_results_reproducible(self):
        encoder = ImageEncoder(image_format="jpeg")
        for raw, image in zip(raw_images, images):
            decoded = encoder.binary_to_array(image)
            assert np.array_equal(raw, decoded)

    @pytest.mark.integration_elastic_search
    @mock.patch('impl.storage.source_image_storage.config')
    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.search_words.search_terms_creator.config_descriptors')
    def test_integration_image_processor(self,
                                         config_descr, config_region, config_src,
                                         unique_temp_index, another_unique_temp_index,
                                         temp_location_for_storage):
        config_src.ELASTIC_SOURCE_IMAGES_INDEX = unique_temp_index
        config_src.ELASTIC_SOURCE_IMAGES_TYPE = "images_" + unique_temp_index
        config_src.FILE_SERVICE_PARAMETERS = {
            "driver_name": "local",
            "storage_driver_parameters": {
                "key": temp_location_for_storage,
            },
            "container_name": "container",
        }
        config_region.ELASTIC_DESCRIPTOR_INDEX = another_unique_temp_index
        config_region.ELASTIC_DESCRIPTOR_TYPE = "descriptors_" + another_unique_temp_index
        config_descr.LENGTH_OF_WORD = 2
        config_descr.NUMBER_OF_LEVELS = 4
        config_descr.DESCRIPTOR_LENGTH = 16 * 3

        processor = ImageProcessorFacade(flush_data=True)
        res1 = processor.find_and_add_by_image(images[0], SourceImageMetadata('path1'))
        assert res1[0]['found'] == []
        assert res1[1]['found'] == []

        res2 = processor.find_and_add_by_image(images[1], SourceImageMetadata('path2'))
        similar2_0 = res2[0]['found']
        similar2_1 = res2[1]['found']
        # one is found. subimages from the first query have to have the same descriptor.
        # But they are processed independently thus can both are added
        assert len(similar2_0) == 2
        assert similar2_0[0]["distance"] == 0  # descriptors are equivalent
        assert similar2_0[1]["distance"] == 0  # descriptors are equivalent
        assert len(similar2_1) == 2
        assert similar2_1[0]["distance"] == 3.0  # descriptors are different equivalent
        assert similar2_1[1]["distance"] == 3.0  # descriptors are different equivalent

        res3 = processor.find_and_add_by_image(images[0], SourceImageMetadata('path3'))
        res4 = processor.find_and_add_by_image(images[2], SourceImageMetadata('path4'))

    @pytest.mark.integration_elastic_search
    @mock.patch('impl.storage.source_image_storage.config')
    @mock.patch('impl.storage.region_repository.config')
    @mock.patch('impl.storage.search_words.search_terms_creator.config_descriptors')
    def test_integration_add_and_find(self,
                                      config_descr, config_region, config_src,
                                      unique_temp_index, another_unique_temp_index,
                                      temp_location_for_storage):
        config_src.ELASTIC_SOURCE_IMAGES_INDEX = unique_temp_index
        config_src.ELASTIC_SOURCE_IMAGES_TYPE = "images_" + unique_temp_index
        config_src.FILE_SERVICE_PARAMETERS = {
            "driver_name": "local",
            "storage_driver_parameters": {
                "key": temp_location_for_storage,
            },
            "container_name": "container",
        }
        config_region.ELASTIC_DESCRIPTOR_INDEX = another_unique_temp_index
        config_region.ELASTIC_DESCRIPTOR_TYPE = "descriptors_" + another_unique_temp_index
        config_descr.LENGTH_OF_WORD = 2
        config_descr.NUMBER_OF_LEVELS = 4
        config_descr.DESCRIPTOR_LENGTH = 16 * 3

        processor = ImageProcessorFacade(flush_data=True)
        url = 'path1'
        processor.add_by_image(images[0], SourceImageMetadata(url))

        res2 = processor.find_by_image(images[0])
        saved_source_id = res2[0]['found'][0]['source_id']
        assert res2 == [
            {
                'region': 0,
                'found': [
                    found_result(0.0, saved_source_id, url),
                    found_result(0.0, saved_source_id, url)
                ]
            },
            {
                'region': 1,
                'found': [
                    found_result(0.0, saved_source_id, url),
                    found_result(0.0, saved_source_id, url)
                ]
            }
        ]

        res3 = processor.find_by_image(images[1])
        assert res3 == [
            {
                'region': 0,
                'found': [
                    found_result(0.0, saved_source_id, url),
                    found_result(0.0, saved_source_id, url)
                ]
            },
            {
                'region': 1,
                'found': [
                    found_result(3.0, saved_source_id, url),
                    found_result(3.0, saved_source_id, url)
                ]
            }
        ]

        res4 = processor.find_by_image(images[2])
        assert res4 == [
            {
                'region': 0,
                'found': [
                    found_result(3.0, saved_source_id, url),
                    found_result(3.0, saved_source_id, url)
                ]
            },
            {
                'region': 1,
                'found': [
                    found_result(3.0, saved_source_id, url),
                    found_result(3.0, saved_source_id, url)
                ]
            }
        ]