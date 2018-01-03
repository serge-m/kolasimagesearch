from io import BytesIO
from typing import List, Dict

from PIL import Image

from impl.domain.source_image_metadata import SourceImageMetadata, EMPTY_METADATA
from impl.feature_engine.subimage_feature_engine import SubimageFeatureEngine
from impl.processors_factory import ProcessorsFactory
from impl.search.cleaned_search_result import CleanedSearchResult
from impl.search.descriptor_search import DescriptorSearch
from impl.storage.source_image_storage import SourceImageStorage
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG']


class WrongImageError(Exception):
    pass


def normalize(binary: bytes) -> bytes:
    stream = BytesIO(binary)
    try:
        image = Image.open(stream)
    except IOError as e:
        raise ImageProcessorError('Failed to parse file as image image') from e

    if image.format not in ALLOWED_IMAGE_FORMATS:
        raise ImageProcessorError('Image format {} is not supported. '
                                  'Supported formats: {}'.format(image.format, ','.join(ALLOWED_IMAGE_FORMATS)))

    return binary


class ImageProcessor:
    def __init__(self, processors_factory=ProcessorsFactory(), flush_data=False):
        self._source_image_storage = SourceImageStorage(flush_data=flush_data)
        extractor = processors_factory.create_feature_extractor()
        self._feature_engine = SubimageFeatureEngine(extractor,
                                                     processors_factory.create_subimage_extractor())
        self._search_service = DescriptorSearch(flush_data=flush_data,
                                                descriptor_shape=extractor.descriptor_shape())

    def build_search(self, image: bytes, metadata: SourceImageMetadata, save: bool) -> List[CleanedSearchResult]:
        normalized = normalize(image)
        list_search_results = self._build_search_results(normalized)
        if save:
            if not metadata or metadata is EMPTY_METADATA:
                raise ValueError("Non empty metadata must be specified")
            reference_to_source = self._source_image_storage.save_source_image(normalized, metadata)
            self._save_missing_regions(list_search_results, reference_to_source)
        return list_search_results

    def _build_search_results(self, normalized: bytes) -> List[CleanedSearchResult]:
        image_regions = self._feature_engine.extract_features(normalized)
        list_search_results = [self._search_service.find_similar_for_region(image_region) for image_region in
                               image_regions]
        return list_search_results

    def _save_missing_regions(self, list_search_results: List[CleanedSearchResult], reference_to_source: str):
        for search_result in list_search_results:
            if search_result.has_good_match():
                # TODO: implement extending references list for the existing saved region
                logger.info('Region {} already exists, skipping'.format(search_result.get_query_region()))
            else:
                region_reference = self._search_service.add_region(search_result.get_query_region(),
                                                                   reference_to_source)
                logger.info("Added new region with reference {}".format(region_reference))

    def build_search_output(self, list_search_results):
        return _build_search_output(self._source_image_storage, list_search_results)


def _build_search_output(source_image_storage, list_search_results: List[CleanedSearchResult]) -> List[Dict]:
    return [
        {
            "region": region_idx,
            "found": _get_references(source_image_storage, search_result)
        }
        for region_idx, search_result in enumerate(list_search_results)
    ]


def _get_references(source_image_storage, search_result: CleanedSearchResult) -> List[Dict[str, object]]:
    similar = search_result.get_similar()

    return [{"distance": x.distance,
             "source_id": x.source_id,
             "metadata": source_image_storage.get_metadata_by_id(x.source_id).to_dict()
             } for x in similar]


class ImageProcessorError(Exception):
    pass



