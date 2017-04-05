from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.feature_extractor import HistogramFeatureExtractor
from impl.feature_engine.subimage_extractor import VerticalSplit
from impl.feature_engine.subimage_feature_engine import SubimageFeatureEngine
from impl.descriptor_search import DescriptorSearch
from impl.storage.source_image_storage import SourceImageStorage


def normalize(image: bytes) -> bytes:
    return image


class ImageProcessor:
    def __init__(self):
        self._source_image_storage = SourceImageStorage()
        self._feature_engine = SubimageFeatureEngine(HistogramFeatureExtractor(), VerticalSplit())
        self._feature_search = DescriptorSearch()

    def process(self, image: bytes, metadata: SourceImageMetadata):
        normalized = normalize(image)
        ref_source = self._source_image_storage.save_source_image(normalized, metadata)
        descriptors = self._feature_engine.extract_features(normalized, ref_source)
        return self._feature_search.find_similar(descriptors)

