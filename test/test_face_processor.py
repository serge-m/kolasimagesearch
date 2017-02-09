from unittest import mock

from face_search.face_processor import FaceProcessor
from face_search.impl.descriptor import Descriptor
from face_search.impl.face import Face
from face_search.impl.source_image_metadata import SourceImageMetadata

expected_search_result = {"results": [{"something": "value"}, {"something2": "value2"}]}


class TestFaceProcessor:
    image = b"encoded image"
    expected_normalized = image
    ref_source = "reference to stored source image"
    metadata = SourceImageMetadata()
    list_faces = [Face(), Face()]
    list_descriptors = [Descriptor(), Descriptor(), Descriptor()]

    @mock.patch('face_search.face_processor.FaceDetector', spec=True)
    @mock.patch('face_search.face_processor.FeatureExtractor', spec=True)
    @mock.patch('face_search.face_processor.FeatureSearch', spec=True)
    @mock.patch('face_search.face_processor.SourceImageStorage', spec=True)
    def test1(self, source_image_storage, feature_search, feature_extractor, face_detector):
        source_image_storage.return_value.save_source_image.return_value = self.ref_source
        face_detector.return_value.detect_faces.return_value = self.list_faces
        feature_extractor.return_value.process_faces.return_value = self.list_descriptors
        feature_search.return_value.find_similar.return_value = expected_search_result

        result = FaceProcessor().process(self.image, self.metadata)

        feature_search.assert_called_once_with()
        feature_search.return_value.find_similar.assert_called_once_with(self.list_descriptors)
        feature_extractor.assert_called_once_with()
        feature_extractor.return_value.process_faces.assert_called_once_with(self.list_faces)
        face_detector.assert_called_once_with()
        face_detector.return_value.detect_faces.assert_called_once_with(self.expected_normalized, self.ref_source)
        source_image_storage.assert_called_once_with()
        source_image_storage.return_value.save_source_image.assert_called_once_with(self.expected_normalized, self.metadata)
        assert result == expected_search_result
