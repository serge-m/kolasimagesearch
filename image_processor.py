from typing import List, Dict

from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.subimage_feature_engine import SubimageFeatureEngine
from impl.processors_factory import ProcessorsFactory
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.search.descriptor_search import DescriptorSearch
from impl.storage.source_image_storage import SourceImageStorage
import requests
import logging

logger = logging.getLogger(__name__)


def normalize(image: bytes) -> bytes:
    return image


class ImageProcessor:
    def __init__(self, processors_factory=ProcessorsFactory(), flush_data=False):
        self._source_image_storage = SourceImageStorage(flush_data=flush_data)
        extractor = processors_factory.create_feature_extractor()
        self._feature_engine = SubimageFeatureEngine(extractor,
                                                     processors_factory.create_subimage_extractor())
        self._search_service = DescriptorSearch(save_data=True, flush_data=flush_data,
                                                descriptor_shape=extractor.descriptor_shape())

    def add_and_search(self, image: bytes, metadata: SourceImageMetadata) -> List[Dict[str, object]]:
        normalized = normalize(image)
        ref_source = self._source_image_storage.save_source_image(normalized, metadata)
        image_regions = self._feature_engine.extract_features(normalized, ref_source)
        list_results = self._search_service.find_similar(image_regions)
        return [
            {
                "region": region_idx,
                "found": self._get_references(search_result)
            }
            for region_idx, search_result in enumerate(list_results)
            ]

    def add(self, url: str):
        logger.info('Adding image <<{}>> to the database'.format(url))
        image = download_image(url)
        metadata = SourceImageMetadata(path=url)
        normalized = normalize(image)
        ref_source = self._source_image_storage.save_source_image(normalized, metadata)
        self._feature_engine.extract_features(normalized, ref_source)

    def _get_references(self, search_result: CleanedSearchResult) -> List[Dict[str, object]]:
        similar = search_result.get_similar()

        return [{"distance": x.distance,
                 "source_id": x.source_id,
                 "metadata": self._source_image_storage.get_metadata_by_id(x.source_id).to_dict()
                 } for x in similar]


class ImageProcessorError(Exception):
    pass


def download_image(url: str):
    timeout = 5
    max_size = 3000000
    r = requests.get(url, timeout=timeout, stream=True)
    content = r.raw.read(max_size + 1, decode_content=True)
    if len(content) > max_size:
        raise ImageProcessorError('File is too large')
    return content
