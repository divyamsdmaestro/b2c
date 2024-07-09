"""
Contains modules related to the Azure Media Services integration.

Note:
     Previously for video streaming, MUX was being used. Later due to cost
     related issues, video streaming was migrated to Azure.

Azure Video Streaming Steps:
    1. Authenticate
    2. Upload/Create an asset(video)                        => File1
    3. Encode the asset to be streamed                      => File1-Encoded
    4. Create a streaming locator for the encoded asset

Integration Architecture:
    Azure Media Services python-sdk does not provide helpers for all the steps
    mentioned above.

    Steps 1,2,3 will be done using the sdk and 4 using their raw rest-api.

References:
    SDK: https://docs.microsoft.com/en-us/azure/media-services/latest/encode-basic-encoding-python-quickstart
    REST: https://docs.microsoft.com/en-us/azure/media-services/latest/stream-files-tutorial-with-rest#prerequisites
"""
