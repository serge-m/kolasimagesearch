import os
import json

FILE_SERVICE_PARAMETERS = {
    "driver_name": os.environ.get("driver_name", "local"),
    "storage_driver_parameters": {
        "key": os.environ.get("driver_key", "./"),
    },
    "container_name": os.environ.get("container_name", "default"),
}

ELASTIC_URL = "http://localhost:9200"
ELASTIC_SOURCE_IMAGES_INDEX = "index"
ELASTIC_SOURCE_IMAGES_TYPE = "sources"
ELASTIC_REGIONS_INDEX = "index"
ELASTIC_REGIONS_TYPE = "regions"
ELASTIC_DESCRIPTOR_INDEX = "index"
ELASTIC_DESCRIPTOR_TYPE = "descriptors"

FEATURE_EXTRACTOR_MODULE = os.environ.get("feature_extractor", "impl.feature_engine")
SUBIMAGE_EXTRACTOR_MODULE = os.environ.get("subimage_extractor", "impl.feature_engine")

FEATURE_EXTRACTOR_PARAMETERS = json.loads(os.environ.get("feature_extractor_params", "{}"))
SUBIMAGE_EXTRACTOR_PARAMETERS = json.loads(os.environ.get("subimage_extractor_params", "{}"))
