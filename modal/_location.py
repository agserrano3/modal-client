# Copyright Modal Labs 2022
from enum import Enum

from modal_proto import api_pb2

from .exception import InvalidError


class CloudProvider(Enum):
    AWS = api_pb2.CLOUD_PROVIDER_AWS
    GCP = api_pb2.CLOUD_PROVIDER_GCP
    AUTO = api_pb2.CLOUD_PROVIDER_AUTO
    OCI = api_pb2.CLOUD_PROVIDER_OCI


def display_location(cloud_provider: "api_pb2.CloudProvider.V") -> str:
    if cloud_provider == api_pb2.CLOUD_PROVIDER_GCP:
        return "GCP (us-east1)"
    elif cloud_provider == api_pb2.CLOUD_PROVIDER_AWS:
        return "AWS (us-east-1)"
    else:
        return ""
