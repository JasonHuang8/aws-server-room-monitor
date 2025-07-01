import json
import boto3
import os
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timezone
from utils.config_loader import load_config


# Initialize the S3 client
s3 = boto3.client('s3')


def lambda_handler(event, context):
    """AWS Lambda function to process sensor data from IoT devices."""
    try:
        # Load configuration and get bucket
        config = load_config()
        logger.debug(f"Loaded config: {config}")
        bucket_name = config.get("s3_bucket", "sensor-data-bucket")
        
        # Extract sensor data
        device_id = event.get("device_id", "unknown")
        temperature = event.get("temperature", 0)
        humidity = event.get("humidity", 0)
        vibration = event.get("vibration", 0)
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z").replace(":", "-")

        # Determine if the data is anomalous
        is_anomaly = temperature > 90 or vibration > 0.7

        payload = {
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "vibration": vibration,
            "timestamp": timestamp,
            "alert": is_anomaly,
            "note": "Anomaly detected" if is_anomaly else "Normal"
        }

        # Serialize to JSON and define key prefix
        key_prefix = "raw/"
        key = f"{key_prefix}{device_id}/{timestamp}.json"

        if device_id == "unknown":
            logger.warning("Device ID is unknown; using fallback ID.")

        # Upload to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=json.dumps(payload),
            ContentType='application/json'
        )

        if is_anomaly:
            key_prefix = "alerts/"
            key = f"{key_prefix}{device_id}/{timestamp}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=json.dumps(payload),
                ContentType='application/json'
            )

        # Send SNS notification if anomaly detected
        if is_anomaly:
            try:
                sns_arn = os.environ.get("SNS_TOPIC_ARN")
                if sns_arn:
                    sns = boto3.client("sns")
                    sns.publish(
                        TopicArn=sns_arn,
                        Subject="⚠️ Sensor Alert Detected",
                        Message=json.dumps(payload, indent=2)
                    )
                    logger.info("SNS alert published successfully.")
                else:
                    logger.warning("SNS_TOPIC_ARN not set in environment variables.")
            except Exception as sns_err:
                logger.error(f"Failed to publish to SNS: {str(sns_err)}")

        logger.info(f"Stored payload in {key}")
        return {
            "statusCode": 200,
            "body": json.dumps(payload)
        }

    except Exception as e:
        logger.error(f"Error during Lambda execution: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
