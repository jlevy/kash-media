import os

from flowmark import Wrap
from prettyfmt import fmt_lines

from kash.config.logger import get_logger
from kash.config.text_styles import COLOR_STATUS
from kash.exec import kash_action
from kash.exec.preconditions import has_html_body
from kash.kits.media.utils.s3_utils import (
    invalidate_s3_urls_in_cf,
    map_s3_urls_to_public_urls,
    s3_upload_path,
)
from kash.model import ActionInput, ActionResult, common_params
from kash.shell.output.shell_output import cprint
from kash.utils.common.url import Url
from kash.utils.errors import InvalidInput
from kash.workspaces import current_ws

log = get_logger(__name__)


@kash_action(precondition=has_html_body, params=common_params("s3_bucket", "s3_prefix"))
def s3_upload(
    input: ActionInput, s3_bucket: str | None = None, s3_prefix: str | None = None
) -> ActionResult:
    """
    Uploads one or more local files/directories (items) to an S3 bucket.
    Requires S3 bucket and optional prefix configured in the action input.
    Uses AWS credentials configured for boto3.
    As a convenience, also looks for and invalidates CloudFront distributions
    if they are found for the uploaded files.
    """

    bucket = s3_bucket or os.getenv("S3_BUCKET")
    prefix = s3_prefix or os.getenv("S3_PREFIX")
    if not bucket or not prefix:
        raise InvalidInput(
            "Must specify --s3_bucket and --s3_prefix or set S3_BUCKET and S3_PREFIX environment variables"
        )
    prefix = prefix.strip("/")
    target_folder = f"s3://{bucket}/{prefix}/"

    log.message("Starting S3 upload to: %s", target_folder)

    ws = current_ws()

    uploaded_s3_urls: list[Url] = []
    for item in input.items:
        if not item.store_path:
            raise InvalidInput(f"Missing store_path for item: {item}")
        local_path = ws.base_dir / item.store_path
        uploaded_s3_urls.extend(s3_upload_path(local_path=local_path, bucket=bucket, prefix=prefix))

    cprint(
        f"Uploaded files:\n{fmt_lines(uploaded_s3_urls)}", style=COLOR_STATUS, text_wrap=Wrap.NONE
    )

    # As a convenience check for public URLs if we can find them.
    public_urls: dict[Url, Url | None] = map_s3_urls_to_public_urls(uploaded_s3_urls)
    if public_urls.values():
        cprint(
            f"Public URLs for these S3 objects:\n{fmt_lines(public_urls.values())}",
            style=COLOR_STATUS,
            text_wrap=Wrap.NONE,
        )

        # If paths are public, also try to invalidate CloudFront distributions.
        try:
            invalidation_results = invalidate_s3_urls_in_cf(uploaded_s3_urls)
            log.warning("Invalidated CloudFront distributions: %s", invalidation_results)
        except RuntimeError as e:
            log.warning("Failed to invalidate CloudFront distributions: %s", e)

    return ActionResult(items=input.items)
