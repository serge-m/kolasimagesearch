import os

FILE_SERVICE_URL = "http://localhost:9333/"
ELASTIC_URL = "http://localhost:9200"
ELASTIC_SOURCE_IMAGES_INDEX = "index"
ELASTIC_SOURCE_IMAGES_TYPE = "sources"
ELASTIC_REGIONS_INDEX = "index"
ELASTIC_REGIONS_TYPE = "regions"
ELASTIC_DESCRIPTOR_INDEX = "index"
ELASTIC_DESCRIPTOR_TYPE = "descriptors"

FEATURE_EXTRACTOR_MODULE = os.environ.get("feature_extractor", "impl.feature_engine")
SUBIMAGE_EXTRACTOR_MODULE = os.environ.get("subimage_extractor", "impl.feature_engine")
