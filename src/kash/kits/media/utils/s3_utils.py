import logging
import mimetypes
from pathlib import Path

import boto3

from kash.utils.errors import InvalidInput

log = logging.getLogger(__file__)


def s3_upload_path(local_path: Path, bucket: str, prefix: str = "") -> list[str]:
    """
    Uploads a local file or directory contents to an S3 bucket prefix.
    Returns list of S3 URLs for the uploaded files.

    Requires AWS credentials configured via environment variables (e.g.,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_REGION)
    or other standard boto3 credential methods.
    """
    if not local_path.exists():
        raise InvalidInput(f"local_path must exist: {local_path}")

    s3_client = boto3.client("s3")
    uploaded_s3_urls: list[str] = []

    # Normalize prefix.
    prefix = prefix.strip("/")
    s3_folder = f"s3://{bucket}/{prefix}"

    def _upload_file(file_path: Path, key_prefix: str):
        # For single file uploads directly, use the filename as the base key
        # For directory uploads, use the relative path
        if local_path.is_file():
            relative_path = file_path.name
        else:
            relative_path = file_path.relative_to(local_path)

        # Normalize Windows paths.
        key = key_prefix + str(relative_path).replace("\\", "/")

        content_type, _ = mimetypes.guess_type(str(file_path))
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        log.warning("Uploading: %s -> s3://%s/%s", file_path, bucket, key)
        s3_client.upload_file(str(file_path), bucket, key, ExtraArgs=extra_args)
        uploaded_s3_urls.append(f"{s3_folder}/{key}")

    if local_path.is_dir():
        log.info("Uploading directory: %s to %s", local_path, s3_folder)
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                _upload_file(file_path, prefix)
    elif local_path.is_file():
        log.info("Uploading file: %s to %s", local_path, s3_folder)
        _upload_file(local_path, prefix)
    else:
        # This case should ideally not be reached due to the exists() check,
        # but handles potential edge cases like broken symlinks.
        raise ValueError(f"local_path is neither a file nor a directory: {local_path}")

    return uploaded_s3_urls
