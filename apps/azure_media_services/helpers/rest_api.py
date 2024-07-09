import json

from django.conf import settings

from apps.common.helpers import make_http_request, random_n_token

AZURE_REST_API_VERSION = "2020-05-01"
AZURE_MANAGEMENT_API_HOST = "https://management.azure.com"


def get_azure_authorization_string() -> str:
    """
    Returns the `authorization_string` to be used for azure rest-api call.
    Usage in header:
        "Authorization": "{authorization_string}"
    """

    response = make_http_request(
        method="POST",
        url=f"https://login.microsoftonline.com/{settings.AZURE_MS_AAD_TENANT_DOMAIN}/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": settings.AZURE_CLIENT_ID,
            "client_secret": settings.AZURE_CLIENT_SECRET,
            "resource": settings.AZURE_MS_ARM_RESOURCE,
        },
    )
    data = response["data"]

    return f"{data['token_type']} {data['access_token']}"


def create_streaming_locator_for_encoded_asset(
    encoded_asset_name: str,
):
    """
    The `encode_and_pre_process_asset_for_video_streaming` will encode a video
    file for streaming. This function when given the encoded_file_name, will
    create the streaming locator and will return the id.
    """

    streaming_locator_name = random_n_token(n=20)
    response = make_http_request(
        url=f"{AZURE_MANAGEMENT_API_HOST}/subscriptions/{settings.AZURE_MS_SUBSCRIPTION_ID}/resourceGroups/{settings.AZURE_MS_RESOURCE_GROUP}/providers/Microsoft.Media/mediaServices/{settings.AZURE_MS_ACCOUNT_NAME}/streamingLocators/{streaming_locator_name}?api-version={AZURE_REST_API_VERSION}",
        method="PUT",
        headers={
            "Authorization": get_azure_authorization_string(),
            "Content-Type": "application/json",
        },
        data=json.dumps(
            {
                "properties": {
                    "streamingPolicyName": "Predefined_DownloadAndClearStreaming",
                    "assetName": encoded_asset_name,
                    "contentKeys": [],
                    "filters": [],
                }
            }
        ),
    )

    streaming_locator_id = response["data"]["properties"]["streamingLocatorId"]  # noqa
    return streaming_locator_name


def get_streaming_url_and_thumbnail_from_locator_name(
    streaming_locator_name: str,
) -> dict:
    """
    During locator creation, the `create_streaming_locator_for_encoded_asset`
    will return the streaming_locator_name. Given that name this function
    will return the `Hls` streaming url using rest-api.
    """

    response = make_http_request(
        url=f"{AZURE_MANAGEMENT_API_HOST}/subscriptions/{settings.AZURE_MS_SUBSCRIPTION_ID}/resourceGroups/{settings.AZURE_MS_RESOURCE_GROUP}/providers/Microsoft.Media/mediaServices/{settings.AZURE_MS_ACCOUNT_NAME}/streamingLocators/{streaming_locator_name}/listPaths?api-version={AZURE_REST_API_VERSION}",
        method="POST",
        headers={
            "Authorization": get_azure_authorization_string(),
            "Content-Type": "application/json",
        },
    )

    # streaming url
    # ------------------------------------------------------------------------
    hls_streaming_path = None
    for _ in response["data"]["streamingPaths"]:
        if _["streamingProtocol"].lower() == "hls":
            hls_streaming_path = _["paths"][0]  # m3u8-aapl
            break
    assert hls_streaming_path

    # thumbnail image
    # ------------------------------------------------------------------------
    thumbnail_image_path = None
    for url in response["data"]["downloadPaths"]:
        if url.endswith("jpg"):
            thumbnail_image_path = url
            break
    assert thumbnail_image_path

    return {
        "streaming_url": f"https://{settings.AZURE_MS_ACCOUNT_NAME}-inct.streaming.media.azure.net{hls_streaming_path}",
        "thumbnail_url": f"https://{settings.AZURE_MS_ACCOUNT_NAME}-inct.streaming.media.azure.net{thumbnail_image_path}",
    }
