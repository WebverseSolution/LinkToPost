import base64
import requests
import os
from config import IMGBB_API_KEY  # Loaded securely via .env

MAX_IMAGE_SIZE_MB = 16

def upload_to_imgbb(image_file):
    """
    Uploads an image to ImgBB and returns the URL.
    Requires IMGBB_API_KEY in .env or environment.
    """
    try:
        if not IMGBB_API_KEY:
            raise EnvironmentError("IMGBB_API_KEY is not configured. Add it to your .env file or EC2 environment.")

        # Validate image size
        image_file.seek(0, os.SEEK_END)
        size_mb = image_file.tell() / (1024 * 1024)
        if size_mb > MAX_IMAGE_SIZE_MB:
            raise ValueError(f"Image exceeds size limit: {size_mb:.2f}MB > {MAX_IMAGE_SIZE_MB}MB")

        image_file.seek(0)
        img_bytes = image_file.read()
        if not img_bytes:
            raise ValueError("Image file is empty or unreadable.")

        encoded = base64.b64encode(img_bytes).decode("utf-8")

        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            data={"image": encoded},
            timeout=15
        )

        if response.status_code != 200:
            raise ConnectionError(f"ImgBB API Error {response.status_code}: {response.text}")

        result = response.json()
        if result.get("success"):
            return result["data"]["url"]

        raise ValueError(result.get("error", "Unknown upload failure"))

    except requests.exceptions.Timeout:
        raise TimeoutError("Upload request timed out.")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error during upload: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Upload error: {str(e)}")
