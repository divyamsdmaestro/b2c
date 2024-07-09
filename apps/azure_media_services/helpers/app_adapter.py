# pylint: disable=no-member
"""
This file contains functions & helpers that act as an adapter/bridge between
the application, `./rest_api.py` and `./sdk.py` for Azure integration.
"""
import os
from urllib.request import urlopen

from django.conf import settings

from apps.azure_media_services.helpers.rest_api import (
    create_streaming_locator_for_encoded_asset,
    get_streaming_url_and_thumbnail_from_locator_name,
)
from apps.azure_media_services.helpers.sdk import (
    encode_and_pre_process_asset_for_video_streaming,
    upload_a_file_and_create_storage_asset,
)
from apps.common.helpers import random_n_token


def download_file_from_url(public_url: str, file_name=None) -> str:
    """
    Given a public url, this will download the file, keep it in temp root
    and will return the full media path to that file.
    """

    temp_file_name = (
        f"{random_n_token()}.{public_url.split('.')[-1]}"  # noqa
        if not file_name
        else file_name
    )  # {random}.png
    temp_file_path = f"{settings.TEMP_ROOT}/{temp_file_name}"

    file = urlopen(public_url)  # nosec
    with open(temp_file_path, "wb") as output:
        output.write(file.read())

    return temp_file_path


def get_azure_streaming_config_from_public_url(video_public_url: str) -> dict:
    """
    Given the public video url, this function will work as an adapter
    and use the `./rest_api.py` & `./sdk.py` to get the streaming
    config from azure media services.

    The streaming config will contain, the assets name, locator
    name and the streaming url name.
    """

    file_path = download_file_from_url(public_url=video_public_url)

    # plain upload
    print("Asset Upload")  # noqa
    azure_storage_file_name = upload_a_file_and_create_storage_asset(
        file_path=file_path
    )

    # encod that plain upload and create new asset
    print("Asset Being Encoded")  # noqa
    azure_storage_file_name_encoded = encode_and_pre_process_asset_for_video_streaming(
        asset_name_to_encode=azure_storage_file_name
    )

    # create streaming locator
    print("Streaming Locator Creation")  # noqa
    streaming_locator_name = create_streaming_locator_for_encoded_asset(
        encoded_asset_name=azure_storage_file_name_encoded
    )

    # get streaming url from locator
    print("Streaming Locator Retrieve")  # noqa
    streaming_url_and_thumbnail_url = get_streaming_url_and_thumbnail_from_locator_name(
        streaming_locator_name=streaming_locator_name
    )

    # post-processing & cleaning
    os.remove(file_path)

    return {
        "azure_streaming_url": streaming_url_and_thumbnail_url["streaming_url"],
        "azure_thumbnail_url": streaming_url_and_thumbnail_url["thumbnail_url"],
        "azure_streaming_locator_name": streaming_locator_name,
        "azure_storage_file_name_encoded": azure_storage_file_name_encoded,
        "azure_storage_file_name": azure_storage_file_name,
    }
