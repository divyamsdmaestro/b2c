from azure.identity import DefaultAzureCredential
from azure.mgmt.media import AzureMediaServices
from azure.mgmt.media.models import (
    Asset,
    BuiltInStandardEncoderPreset,
    Job,
    JobInputAsset,
    JobOutputAsset,
    Transform,
    TransformOutput,
)
from azure.storage.blob import BlobServiceClient
from django.conf import settings

from apps.common.helpers import pause_thread, random_n_token


def get_file_name(file_path: str, with_extension=False) -> str:
    """
    Given the full path of a file. This will return the file name of the same
    based on the passed parameters.

    Ex:
        `~/Downloads/filename.png` => `filename.png` or `filename`
    """

    file_name_with_extension = file_path.split("/")[-1]
    return (
        file_name_with_extension
        if with_extension
        else file_name_with_extension.split(".")[0]
    )


def get_azure_ms_client():
    """Returns the azure media services - python sdk client."""

    return AzureMediaServices(
        DefaultAzureCredential(), settings.AZURE_MS_SUBSCRIPTION_ID
    )


def upload_a_file_and_create_storage_asset(file_path: str) -> str:
    """
    Given a file path, this will upload that file using blob and
    crates an asset in azure storage container.

    Returns the name of the asset that was created.
    """

    # pre-process
    asset_name = get_file_name(file_path=file_path, with_extension=False)
    asset_name = f"{asset_name}-{random_n_token()}"

    asset = Asset()
    asset_object = get_azure_ms_client().assets.create_or_update(
        settings.AZURE_MS_RESOURCE_GROUP,
        settings.AZURE_MS_ACCOUNT_NAME,
        asset_name,
        asset,
    )
    blob_container_name_for_asset = "asset-" + asset_object.asset_id  # syntax

    blob_service_client = BlobServiceClient.from_connection_string(
        settings.AZURE_MS_STORAGE_ACCOUNT_CONNECTION
    )
    blob_client = blob_service_client.get_blob_client(
        blob_container_name_for_asset,
        get_file_name(file_path=file_path, with_extension=True),
    )
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

    return asset_name


def encode_and_pre_process_asset_for_video_streaming(asset_name_to_encode: str) -> str:
    """
    In `upload_a_file_and_create_storage_asset` the video file will be uploaded
    and created as an asset. In order for it be streamed, the asset has to
    be pre-processed in azure. This function will trigger the same.
    """

    client = get_azure_ms_client()
    encoded_asset_name = f"{asset_name_to_encode}-encoded"  # output asset name

    # creates the asset
    client.assets.create_or_update(
        settings.AZURE_MS_RESOURCE_GROUP,
        settings.AZURE_MS_ACCOUNT_NAME,
        encoded_asset_name,
        Asset(),
    )

    # wrapper for the encoding jobs | Transforms
    # transform_name = f"{asset_name_to_encode}_transform"
    transform_name = "encode_and_pre_process_transform"
    transform = Transform()
    transform.outputs = [
        TransformOutput(
            preset=BuiltInStandardEncoderPreset(preset_name="H264MultipleBitrate720p")
        )
    ]
    transform = client.transforms.create_or_update(  # noqa
        resource_group_name=settings.AZURE_MS_RESOURCE_GROUP,
        account_name=settings.AZURE_MS_ACCOUNT_NAME,
        transform_name=transform_name,
        parameters=transform,
    )

    # workers inside the transform | Jobs
    # job_name = f"{transform_name}_job"
    job_name = f"{asset_name_to_encode}_job"
    input_asset = JobInputAsset(asset_name=asset_name_to_encode)
    output_asset = JobOutputAsset(asset_name=encoded_asset_name)
    transform_job: Job = client.jobs.create(  # noqa
        settings.AZURE_MS_RESOURCE_GROUP,
        settings.AZURE_MS_ACCOUNT_NAME,
        transform_name,
        job_name,
        parameters=Job(input=input_asset, outputs=[output_asset]),
    )

    print("Waiting For Job Completion")  # noqa
    countdown_and_wait_for_encode_and_pre_process_asset(
        job_name=job_name, transform_name=transform_name
    )

    return encoded_asset_name


def countdown_and_wait_for_encode_and_pre_process_asset(
    job_name, transform_name, time_to_wait=10  # time to wait in seconds
):
    while time_to_wait:
        mins, secs = divmod(time_to_wait, 60)
        timer = f"{mins:02d}:{secs:02d}"
        print(timer, end="\r")  # noqa
        pause_thread(seconds=1)  # time.sleep
        time_to_wait -= 1

    job_current = get_azure_ms_client().jobs.get(
        settings.AZURE_MS_RESOURCE_GROUP,
        settings.AZURE_MS_ACCOUNT_NAME,
        transform_name,
        job_name,
    )

    if job_current.state == "Finished":
        print(job_current.state)  # noqa
        return

    if job_current.state == "Error":
        print(job_current.state)  # noqa
        return  # let it break | captured in exceptions

    else:
        print(job_current.state)  # noqa
        countdown_and_wait_for_encode_and_pre_process_asset(
            time_to_wait=10, job_name=job_name, transform_name=transform_name
        )
