# Server Room Environmental Monitor
![Built with AWS](https://img.shields.io/badge/Built%20with-AWS-orange)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Serverless](https://img.shields.io/badge/Architecture-Serverless-green)
![License](https://img.shields.io/badge/License-MIT-green)

## Summary 
This project is a cloud-native, production-grade server room monitoring pipeline built entirely on AWS. It simulates real-time environmental telemetry—including temperature, humidity, and vibration—and streams the data to AWS IoT Core for ingestion. From there, a Lambda function processes the data and routes it to Amazon S3 or triggers alerts via Amazon SNS based on configurable anomaly detection thresholds.

I designed and implemented this system to demonstrate my ability to build scalable, event-driven cloud architectures using Python and core AWS services. It highlights practical skills in serverless computing, IoT data ingestion, observability, and fault-tolerant design—capabilities that mirror those used in real-world edge monitoring and data center infrastructure. While similar in concept to enterprise solutions like AWS Kinesis, Apache Kafka, or Azure Event Hubs, this pipeline is built for minimal cost (fully free-tier compatible) and significantly lower operational complexity.

## Purpose

This project is part of my broader effort to deepen my expertise in cloud engineering, with a focus on AWS infrastructure. I’m simulating the type of telemetry workflows used in edge monitoring or data center health systems—critical in high-availability environments like AWS EC2 or enterprise server fleets.

Throughout this project, I actively leveraged AI as a development assistant—using it to accelerate learning curves around new AWS services and Python libraries. AI helped streamline low-level tasks like generating test cases or debugging syntax, but I took ownership of the architectural design, direction, and integration across components. This project reflects not only technical execution but also my growing skill in using AI as a tool. I got to further deepen my understanding of where it excels, and more importantly, where human-driven planning and decision-making are irreplaceable.

## Key AWS Services Used

- **AWS IoT Core** – MQTT broker for ingesting sensor telemetry
- **AWS Lambda** – Serverless compute to process and evaluate incoming data
- **Amazon S3** – Durable object storage for logs and alerts
- **Amazon SNS** – Push-based alerting mechanism (email/SMS)
- **AWS CloudWatch** – Metrics, logs, and observability
- **AWS IAM** – Roles and policies built starting from least privilege to manage secure access between components (IoT → Lambda → S3/SNS)
- *(Optional)*: EC2, AWS Greengrass, Athena, QuickSight

## How it Works

Simulated sensor data from a Python script is streamed and ingested into AWS IoT Core, processed serverlessly via Lambda, and stored in S3 or used to trigger real-time alerts via SNS. Logs and metrics are also sent to CloudWatch for further function analysis.

## Architecture Diagram

![Architecture](docs/architecture_diagram.png)

## Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/aws-server-room-monitor.git
   cd aws-server-room-monitor
   ```

2. **Set up Python virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   
   If you're new to Python virtual environments, this creates an isolated environment for dependencies. Learn more [here](https://docs.python.org/3/library/venv.html).

3. **Configure AWS credentials**  
   Ensure you have AWS CLI installed and configured:
   ```bash
   aws configure
   ```

4. **Set up environment variables**  
   Create a `.env` file in the root directory with the following required fields:
   ```
   AWS_IOT_ENDPOINT=your-iot-endpoint.amazonaws.com
   CERT_PATH=certs/your-certificate.pem.crt
   KEY_PATH=certs/your-private.pem.key
   CA_PATH=certs/Amazon-root-CA.pem
   AWS_REGION=your-region
   SNS_TOPIC_ARN=arn:aws:sns:your-region:account-id:your-topic
   ```

   Make sure these paths match your actual certificate files. You can obtain these from AWS IoT when creating and downloading your device credentials.

   These credentials are required to authenticate the simulator with AWS IoT Core and publish to SNS. Ensure you have completed AWS IoT device setup and downloaded the appropriate credentials.

5. **Run the sensor simulator**  
   Single rack mode:
   ```bash
   python3 simulator/simulate_sensors.py
   ```

   Simulate multiple racks in parallel (optional):
   ```bash
   python3 simulator/simulate_sensors.py --num-racks <int>
   ```

   To test MQTT client, subscribe to sensors/server-room/#.


   #### CLI Flags for simulate_sensors.py

   - `--num-racks` (int): Number of server racks to simulate in parallel. Default is 1.
   - `--device-id` (str): Device ID for single-rack mode. Auto-generated in multi-rack mode.
   - `--min-interval` (int): Minimum interval (in seconds) between messages. Default is 5.
   - `--max-interval` (int): Maximum interval (in seconds) between messages. Default is 10.
   - `--num-messages` (int): Optional cap on the number of messages to send per rack.
   - `--anomaly-rate` (float): Probability [0–1] that a message includes an anomaly. Default is 0.05.

6. **Deploy Lambda function**
   - Copy updated handler for local testing:
     ```bash
     cp lambda/lambda_function.py lambda_deploy/lambda_function.py
     ```
   - Zip and upload for full deployment:
     ```bash
     rm lambda_payload.zip
     zip -r lambda_payload.zip . -x "*.DS_Store" "**/__pycache__/*"
     ```

✅ Tip: To clean up the S3 bucket after a test run, use:
```bash
python3 clean_s3_prefixes.py
```
This removes all uploaded payload logs under the configured S3 prefix.

## Folder Structure

```
aws-server-room-monitor/
├── certs/                    # IoT device certificates and keys
├── cloudformation/           # AWS CloudFormation templates
├── docs/                     # Architecture diagrams, output samples
├── lambda/                   # Lambda source code
├── lambda_deploy/            # Lambda code for deployment
├── simulator/                # MQTT sensor simulator
├── test/                     # Test scripts and test_plan.md
├── test_inputs/              # Sample JSON test cases
├── utils/                    # Helper modules like config loader
├── config.json               # Optional config file for simulation
├── requirements.txt          # Python dependencies
├── LICENSE
└── README.md
```

## Example Payloads & Output

Sample sensor payload:
```json
{
  "device_id": "rack-01",
  "temperature": 78.77,
  "humidity": 54.34,
  "vibration": 0.85,
  "timestamp": "2025-07-13T07:39:44.734603Z"
}
```

Example SNS alert format:
```json
{
  "device_id": "rack-01",
  "temperature": 78.77,
  "humidity": 54.34,
  "vibration": 0.85,
  "timestamp": "2025-07-13T07:39:44.734603Z",
  "alert": true,
  "note": "1 Anomalies Detected: Excessive vibration"
}
```

Additional examples and CloudWatch/S3 output logs are available in the `docs/` and `test_inputs/` folders.

## Roadmap

Phase 0 – Setup & Project Initialization
Set up the project structure, .gitignore, virtual environment, and config files. Connect the repo and prepare the dev environment.

Phase 1 – Sensor Simulator (Python)
Write a Python script to simulate temperature, humidity, and vibration data. This will send data periodically using MQTT.

Phase 2 – AWS IoT Ingestion
Set up AWS IoT Core to receive MQTT messages. Create rules to trigger processing.

Phase 3 – Event-Driven Processing & Alerts
Write a Lambda function to process incoming data, check for anomalies, and send alerts via SNS or log to S3.

Phase 4 – System Testing & Observability
Simulate both normal and abnormal sensor data. Use CloudWatch and logging to verify everything works correctly.

Phase 5 – Documentation & Architecture Diagrams
Write the final README, generate architecture visuals, and document how the system works.

Phase 6 – Extensions & Enhancements
Add optional improvements like ML-based anomaly detection, EC2 deployment, metrics visualization, or CI/CD.

## Extensions & Future Work

- Add CI/CD pipeline for Lambda deployment (GitHub Actions)
- Integrate ML-based anomaly detection
- Buffering via SQS or EventBridge
- Data warehousing via Athena or Redshift
- Visualization via QuickSight or Grafana
- Edge device deployment with AWS Greengrass
