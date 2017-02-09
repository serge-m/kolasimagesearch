from face_search.impl.face_detector import FaceDetector
from face_search.impl.feature_extractor import FeatureExtractor
from face_search.impl.feature_search import FeatureSearch
from face_search.impl.source_image_metadata import SourceImageMetadata
from face_search.impl.source_image_storage import SourceImageStorage


def normalize(image: bytes) -> bytes:
    return image


class FaceProcessor:
    def __init__(self):
        self.source_image_storage = SourceImageStorage()
        self.face_detector = FaceDetector()
        self.feature_extractor = FeatureExtractor()
        self.feature_search = FeatureSearch()

    def process(self, image: bytes, metadata: SourceImageMetadata):
        normalized = normalize(image)
        ref_source = self.source_image_storage.save_source_image(normalized, metadata)
        faces = self.face_detector.detect_faces(normalized, ref_source)
        descriptors = self.feature_extractor.process_faces(faces)
        return self.feature_search.find_similar(descriptors)

