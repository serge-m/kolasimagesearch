from unittest import mock
from unittest.mock import call

import pytest
from kolasimagecommon import FeatureExtractor
from kolasimagecommon import SubimageExtractor

from impl.processors_factory import ProcessorsFactory


@pytest.fixture
def mocked_instance():
    return "some data"


@pytest.fixture
def mocked_class(mocked_instance):
    mocked_class = mock.MagicMock()
    mocked_class.return_value = mocked_instance
    return mocked_class


# noinspection PyShadowingNames
class TestProcessorsFactory:
    mocked_config = mock.MagicMock()
    mocked_config.SUBIMAGE_EXTRACTOR_MODULE = "SUBIMAGE_EXTRACTOR_MODULE11"
    mocked_config.FEATURE_EXTRACTOR_MODULE = "FEATURE_EXTRACTOR_MODULE11"

    mocked_class2 = mock.MagicMock()

    @mock.patch('impl.processors_factory.load_class_from_module')
    def test_processors_factory_gives_subimage_extractor(self, load_class_from_module, mocked_class, mocked_instance):
        load_class_from_module.side_effect = [mocked_class, "bla"]

        extractor = ProcessorsFactory(config=self.mocked_config).create_subimage_extractor()

        assert extractor == mocked_instance
        mocked_class.assert_called_once_with()
        load_class_from_module.assert_has_calls([call(self.mocked_config.SUBIMAGE_EXTRACTOR_MODULE, SubimageExtractor),
                                                 call(self.mocked_config.FEATURE_EXTRACTOR_MODULE, FeatureExtractor)])

    @mock.patch('impl.processors_factory.load_class_from_module')
    def test_processors_factory_gives_feature_extractor(self, load_class_from_module, mocked_class, mocked_instance):
        load_class_from_module.side_effect = ["bla", mocked_class]

        extractor = ProcessorsFactory(config=self.mocked_config).create_feature_extractor()

        assert extractor == mocked_instance
        mocked_class.assert_called_once_with()
        load_class_from_module.assert_has_calls([call(self.mocked_config.SUBIMAGE_EXTRACTOR_MODULE, SubimageExtractor),
                                                 call(self.mocked_config.FEATURE_EXTRACTOR_MODULE, FeatureExtractor)])
