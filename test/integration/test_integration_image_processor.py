from io import BytesIO
from unittest import mock

from image_processor import ImageProcessor
import numpy as np
from PIL import Image
import matplotlib.pylab as plt

# noinspection PyUnresolvedReferences
from impl.storage.source_image_storage import SourceImageStorage
from impl.test.elastic_fixtures import unique_temp_index, another_unique_temp_index, index_name

from impl.domain.source_image_metadata import EMPTY_METADATA

def _combine(image1, image2):
    return np.hstack([image1, image2])


_format = "jpeg"


def numpy_to_binary(image: np.ndarray) -> bytes:
    im = Image.fromarray(np.uint8(image))
    file_like = BytesIO()
    im.save(file_like, format=_format)
    return file_like.getvalue()


def _generate_subimage(color1, color2):
    img = np.zeros([h, w, num_channels], dtype='uint8')

    _put_color(color1, img, w * h // 3)
    _put_color(color2, img, w * h // 3)
    return img


def _put_color(color, img, num_samples):
    y = rs.random_integers(0, h - 1, [num_samples])
    x = rs.random_integers(0, w - 1, [num_samples])
    img[y, x, :] = color


h = 40
w = 50
num_channels = 3

rs = np.random.RandomState(0)


color1 = [128, 0, 255]
color2 = [128, 255, 255]
color3 = [128, 0, 0]
color4 = [0, 120, 0]
image1 = numpy_to_binary(_combine(_generate_subimage(color1, color2), _generate_subimage(color1, color2)))
image2 = numpy_to_binary(_combine(_generate_subimage(color3, color4), _generate_subimage(color3, color4)))
image3 = numpy_to_binary(_combine(_generate_subimage(color1, color2), _generate_subimage(color3, color4)))
image4 = numpy_to_binary(_combine(_generate_subimage(color1, color1), _generate_subimage(color2, color2)))


class TestIntegrationImageProcessor:

    @mock.patch('impl.storage.source_image_storage.config')
    @mock.patch('impl.storage.region_repository.config')
    def test_integration_image_processor(self, c2, c, unique_temp_index, another_unique_temp_index):

        # plt.imshow(img1)
        # plt.show()

        c.ELASTIC_SOURCE_IMAGES_INDEX = unique_temp_index
        c.ELASTIC_SOURCE_IMAGES_TYPE = "images_" + unique_temp_index
        c.FILE_SERVICE_URL = "http://localhost:9333/"
        c2.ELASTIC_DESCRIPTOR_INDEX = another_unique_temp_index
        c2.ELASTIC_DESCRIPTOR_TYPE = "descriptors_" + another_unique_temp_index

        processor = ImageProcessor()
        res1 = processor.process(image1, EMPTY_METADATA)
        res2 = processor.process(image2, EMPTY_METADATA)

        res3 = processor.process(image1, EMPTY_METADATA)
        res4 = processor.process(image2, EMPTY_METADATA)

        print(res1)


