from typing import List

import importlib
import logging
from kolasimagecommon import FeatureExtractor
from kolasimagecommon import SubimageExtractor

import config as default_config


def load_class_from_module(class_path: str, target_class: type) -> type:
    module_path = _get_module_path(class_path)
    class_name = _get_class_name(class_path)
    module = importlib.import_module(module_path)
    loaded_class = getattr(module, class_name)
    if not loaded_class:
        raise RuntimeError("Unable to find class {} in {}".format(class_name, module_path))
    if not issubclass(loaded_class, target_class):
        raise RuntimeError("Class {} must implement {}".format(class_path, target_class))
    return loaded_class


def _get_module_path(class_path):
    return '.'.join(class_path.split('.')[:-1])


def _get_class_name(class_path):
    return class_path.split('.')[-1]


class ProcessorsFactory:
    def __init__(self, config=default_config):
        # TODO add import by class name
        self.cls_subimage_extractor = load_class_from_module(config.SUBIMAGE_EXTRACTOR_MODULE, SubimageExtractor)
        self.cls_feature_extractor = load_class_from_module(config.FEATURE_EXTRACTOR_MODULE, FeatureExtractor)
        self.subimage_extractor_params = config.SUBIMAGE_EXTRACTOR_PARAMETERS
        self.feature_extractor_params = config.FEATURE_EXTRACTOR_PARAMETERS

    def create_feature_extractor(self):
        logger = logging.getLogger(__name__)
        logger.info("Building feature extractor "
                    "from {} with {}".format(self.cls_feature_extractor, self.feature_extractor_params))

        return self.cls_feature_extractor(**self.feature_extractor_params)

    def create_subimage_extractor(self) -> SubimageExtractor:
        logger = logging.getLogger(__name__)
        logger.info("Building subimage extractor "
                    "from {} with {}".format(self.cls_subimage_extractor, self.subimage_extractor_params))

        return self.cls_subimage_extractor(**self.subimage_extractor_params)
