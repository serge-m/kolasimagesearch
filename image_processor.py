from impl.feature_extractor import FeatureExtractor
from impl.feature_search import FeatureSearch
from impl.source_image_metadata import SourceImageMetadata
from impl.source_image_storage import SourceImageStorage


def normalize(image: bytes) -> bytes:
    return image


class ImageProcessor:
    def __init__(self):
        self.source_image_storage = SourceImageStorage()
        self.feature_extractor = FeatureExtractor()
        self.feature_search = FeatureSearch()

    def process(self, image: bytes, metadata: SourceImageMetadata):
        normalized = normalize(image)
        ref_source = self.source_image_storage.save_source_image(normalized, metadata)
        descriptors = self.feature_extractor.extract_features(normalized, ref_source)
        return self.feature_search.find_similar(descriptors)

