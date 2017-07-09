from kolasimagecommon import SubimageExtractor

from impl.processors_factory import ProcessorsFactory


class TestProcessorsFactory:
    def test_processors_factory(self):
        factory = ProcessorsFactory()
        extractor = factory.create_subimage_extractor()

        assert isinstance(extractor, SubimageExtractor)
        # TODO: add tests
