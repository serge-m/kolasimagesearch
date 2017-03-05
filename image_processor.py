from impl.domain.source_image_metadata import SourceImageMetadata
from impl.feature_engine.feature_extractor import HistogramFeatureExtractor
from impl.feature_engine.subimage_extractor import VerticalSplit
from impl.feature_engine.subimage_feature_engine import SubimageFeatureEngine
from impl.feature_search import FeatureSearch
from impl.storage.source_image_storage import SourceImageStorage


def normalize(image: bytes) -> bytes:
    return image


class ImageProcessor:
    def __init__(self):
        self.source_image_storage = SourceImageStorage()
        self.feature_engine = SubimageFeatureEngine(HistogramFeatureExtractor, VerticalSplit)
        self.feature_search = FeatureSearch()

    def process(self, image: bytes, metadata: SourceImageMetadata):
        normalized = normalize(image)
        ref_source = self.source_image_storage.save_source_image(normalized, metadata)
        descriptors = self.feature_engine.extract_features(normalized, ref_source)
        return self.feature_search.find_similar(descriptors)

