from typing import List, Dict

from image_processor import ImageProcessor, ImageProcessorError
from impl.domain.source_image_metadata import SourceImageMetadata, EMPTY_METADATA
import requests
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG']


class ImageProcessorFacade:
    def __init__(self, flush_data=False):
        self.image_processor = ImageProcessor(flush_data=flush_data)

    def find_by_image(self, image: bytes) -> List[Dict[str, object]]:
        list_search_results = self.image_processor.build_search(image, metadata=EMPTY_METADATA, save=False)
        return self.image_processor.build_search_output(list_search_results)

    def find_by_url(self, url: str) -> List[Dict[str, object]]:
        image = download_image(url)
        return self.find_by_image(image)

    def add_by_url(self, url: str):
        image = download_image(url)
        metadata = SourceImageMetadata(path=url)
        self.image_processor.build_search(image, metadata, save=True)

    def add_by_image(self, image: bytes, metadata: SourceImageMetadata):
        self.image_processor.build_search(image, metadata, save=True)

    def find_and_add_by_url(self, url: str) -> List[Dict]:
        image = download_image(url)
        metadata = SourceImageMetadata(path=url)
        return self.find_and_add_by_image(image, metadata)

    def find_and_add_by_image(self, image: bytes, metadata: SourceImageMetadata) -> List[Dict]:
        list_search_results = self.image_processor.build_search(image, metadata, save=True)
        return self.image_processor.build_search_output(list_search_results)


def download_image(url: str):
    timeout = 5
    max_size = 3000000
    r = requests.get(url, timeout=timeout, stream=True)
    content = r.raw.read(max_size + 1, decode_content=True)
    if len(content) > max_size:
        raise ImageProcessorError('File is too large. url: <<{}>>'.format(url))

    return content

