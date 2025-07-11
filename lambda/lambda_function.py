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
if not logger.hasHandlers():
    # If no handlers are set, add the stream handler
    # to avoid duplicate logs in AWS Lambda
    logger.addHandler(handler)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timezone
from utils.config_loader import load_config
from dateutil.parser import parse as parse_datetime


# Initialize the S3 client
s3 = boto3.client('s3')
cloudwatch = boto3.client("cloudwatch")

# Constants for thresholds
TEMP_THRESHOLD_F = 85   # Above this, cooling may be needed
HUMIDITY_LOW = 20       # Below this, risk of static
HUMIDITY_HIGH = 60      # Above this, risk of condensation
VIBRATION_THRESHOLD = 0.5  # Above this, potential mechanical issue


def lambda_handler(event, context):
    """AWS Lambda function to process sensor data from IoT devices."""
    try:
        emit_metric("LambdaExecutions", 1)
        # Load configuration and get bucket
        config = load_config()
        logger.debug(f"Loaded config: {config}")
        bucket_name = config.get("s3_bucket", "sensor-data-bucket")

        # Validate required fields
        required_fields = ["device_id", "temperature", "humidity", "vibration", "timestamp"]
        missing = [f for f in required_fields if f not in event]
        if missing:
            logger.error(f"Missing required fields: {missing}")
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": f"Missing fields: {', '.join(missing)}"}
                    )
            }
        
        # Validate data ranges
        try:
            device_id = event.get("device_id", "unknown")
            temperature = float(event.get("temperature", 0))
            humidity = float(event.get("humidity", 0))
            vibration = float(event.get("vibration", 0))

        except (ValueError, TypeError):
            logger.error("Invalid data types in payload.")
            timestamp = (
                datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
                .replace(":", "-")
            )
            store_payload_to_s3(bucket_name, "invalid/",
                                event, timestamp, device_id)
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Invalid data types",
                    "saved_as": (
                        f"invalid/{device_id}/{timestamp}.json"
                    )
                })
            }

        try:
            timestamp_raw = event.get("timestamp")
            timestamp = (
                parse_datetime(timestamp_raw)
                .astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
                .replace(":", "-")
            )
        except Exception:
            logger.warning("Invalid timestamp format, using current UTC time.")
            timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z").replace(":", "-")

        if not (0 <= humidity <= 100 and 0 <= temperature <= 200
                and 0 <= vibration <= 5):
            logger.warning(
                "Data out of expected range",
                extra={
                    "temperature": temperature,
                    "humidity": humidity,
                    "vibration": vibration
                }
            )
            store_payload_to_s3(bucket_name, "invalid/", event,
                                timestamp, device_id)
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Values out of expected range",
                    "saved_as": f"invalid/{device_id}/{timestamp}.json"
                })
            }

        # Determine if the data is anomalous
        note = []

        if temperature > TEMP_THRESHOLD_F:
            note.append("High temperature")
        if humidity < HUMIDITY_LOW:
            note.append("Low humidity")
        elif humidity > HUMIDITY_HIGH:
            note.append("High humidity")
        if vibration > VIBRATION_THRESHOLD:
            note.append("Excessive vibration")

        is_anomaly = len(note) > 0

        payload = {
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "vibration": vibration,
            "timestamp": timestamp,
            "alert": is_anomaly,
            "note": f"Anomalies: {', '.join(note)}" if note else "Normal"
        }

        if device_id == "unknown":
            logger.warning("Device ID is unknown; using fallback ID.")

        # Upload to S3 raw data bucket
        store_payload_to_s3(bucket_name, "raw/", payload, timestamp, device_id)

        # Check if the data is anomalous. If so, store in alerts bucket
        # and send SNS notification.
        if is_anomaly:
            emit_metric("AnomaliesDetected", 1, device_id)
            store_payload_to_s3(bucket_name, "alerts/", payload,
                                timestamp, device_id)

            try:
                sns_arn = os.environ.get("SNS_TOPIC_ARN")
                if sns_arn:
                    sns = boto3.client("sns")
                    sns.publish(
                        TopicArn=sns_arn,
                        Subject="⚠️ Sensor Alert Detected",
                        Message=json.dumps(payload, indent=2)
                    )
                    logger.info(
                        "SNS alert published",
                        extra={
                            "device_id": device_id,
                            "timestamp": timestamp
                        }
                    )
                else:
                    logger.warning(
                        "SNS_TOPIC_ARN not set in environment variables."
                        )
            except Exception as sns_err:
                logger.error(f"Failed to publish to SNS: {str(sns_err)}")

        logger.info(
            "Payload processed and stored",
            extra={
                "device_id": device_id,
                "timestamp": timestamp
            }
        )
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


# Utility function to store the payload in S3
# with a specific prefix and timestamp.
def store_payload_to_s3(bucket, prefix, payload, timestamp, device_id):
    key = f"{prefix}{device_id}/{timestamp}.json"
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(payload),
            ContentType='application/json'
        )
        logger.info(
            "S3 put_object success",
            extra={"s3_key": key, "bucket": bucket}
        )
    except Exception as e:
        logger.error(f"Failed to store payload in {key}: {e}")


# Utility function to emit custom CloudWatch metrics
# for monitoring Lambda execution and anomalies.
def emit_metric(name, value, device_id, unit="Count"):
    try:
        cloudwatch.put_metric_data(
            Namespace="ServerRoomMonitor",
            MetricData=[{
                "MetricName": name,
                "Value": value,
                "Unit": unit,
                "Dimensions": [{"Name": "DeviceId",
                                "Value": device_id}]
            }]
        )
        logger.info(f"Custom CloudWatch metric emitted: {name} = {value}")
    except Exception as e:
        logger.warning(f"Failed to emit CloudWatch metric {name}: {e}")
