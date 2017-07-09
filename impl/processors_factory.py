from typing import List

import importlib
from kolasimagecommon import FeatureExtractor
from kolasimagecommon import SubimageExtractor

import config


def load_class_from_module(module_path: str, target_class: type) -> type:
    module = importlib.import_module(module_path)
    list_classes = get_all_classes_implementing_interface(module, target_class)
    if not list_classes:
        raise RuntimeError("Unable to find implemented interface {} in {}".format(target_class, module_path))
    if len(list_classes) > 1:
        raise RuntimeError("More then 1 implementation of {} was found in {}".format(target_class, module_path))
    return list_classes[0]


def get_all_classes_implementing_interface(module, target_class: type) -> List[type]:
    results = []
    for attr in dir(module):
        cls = getattr(module, attr)
        if isinstance(cls, type) and issubclass(cls, target_class):
            results.append(cls)
    return results


class ProcessorsFactory:
    def __init__(self):
        # TODO add import by class name
        self.cls_subimage_extractor = load_class_from_module(config.SUBIMAGE_EXTRACTOR_MODULE, SubimageExtractor)
        self.cls_feature_extractor = load_class_from_module(config.FEATURE_EXTRACTOR_MODULE, FeatureExtractor)

    def create_feature_extractor(self):
        return self.cls_feature_extractor()

    def create_subimage_extractor(self) -> SubimageExtractor:
        return self.cls_subimage_extractor()
