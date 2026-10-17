import base64
import requests
from django.conf import settings


def upload_to_imagekit(file_obj, filename, folder="/gallery"):
    """
    Direct HTTP POST to ImageKit.io API using standard requests.
    Completely eliminates all SDK __init__ argument mismatches.
    """
    private_key = getattr(settings, 'IMAGEKIT_PRIVATE_KEY', '').strip()

    # Read binary file data and encode as base64
    file_bytes = file_obj.read()
    file_b64 = base64.b64encode(file_bytes).decode('utf-8')

    upload_url = "https://upload.imagekit.io/api/v1/files/upload"

    # ImageKit authenticates using HTTP Basic Auth: (private_key, '')
    auth = (private_key, '')

    payload = {
        "file": file_b64,
        "fileName": filename,
        "folder": folder,
        "useUniqueFileName": "true",
        "tags": "school_gallery"
    }

    response = requests.post(upload_url, data=payload, auth=auth)
    res_data = response.json()

    if response.status_code not in (200, 201):
        error_msg = res_data.get('message', 'Upload to ImageKit failed')
        raise Exception(error_msg)

    return {
        "url": res_data.get("url"),
        "file_id": res_data.get("fileId")
    }


def delete_from_imagekit(file_id):
    """
    Deletes an asset from ImageKit.io via direct REST API.
    """
    if not file_id:
        return

    private_key = getattr(settings, 'IMAGEKIT_PRIVATE_KEY', '').strip()
    delete_url = f"https://api.imagekit.io/v1/files/{file_id}"
    auth = (private_key, '')

    try:
        requests.delete(delete_url, auth=auth)
    except Exception:
        pass