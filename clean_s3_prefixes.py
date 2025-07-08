import boto3
from utils.config_loader import load_config
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_prefix_objects(bucket, prefix):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    deleted_count = 0
    for page in pages:
        if "Contents" in page:
            objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
            s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})
            deleted_count += len(objects)
    logger.info(f"Deleted {deleted_count} objects under prefix '{prefix}'.")


def main():
    config = load_config()
    bucket = config["s3_bucket"]
    prefixes = config.get("s3_prefixes", ["raw/", "alerts/", "invalid/"])

    for prefix in prefixes:
        delete_prefix_objects(bucket, prefix)


if __name__ == "__main__":
    main()
