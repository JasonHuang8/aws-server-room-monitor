# System Test Plan – AWS Server Room Monitoring

This document outlines the test matrix for validating the end-to-end functionality of the monitoring system: IoT → Lambda → S3/SNS.

---

## ✅ Test Cases

| Test Case           | Input Description                                               | Expected Lambda Action                          | S3 Storage      | SNS Alert Sent | Notes                       |
|---------------------|------------------------------------------------------------------|--------------------------------------------------|------------------|----------------|-----------------------------|
| 1. Normal Input      | All values within threshold                                      | Parse and log                                    | ✅ `raw/` only    | ❌ No alert     |                            |
| 2. High Temp Alert   | `temperature = 95.0°F`                                           | Flag as anomaly, log                             | ✅ `alerts/`      | ✅ Yes          |                            |
| 3. High Vibration    | `vibration = 0.75`                                               | Flag as anomaly, log                             | ✅ `alerts/`      | ✅ Yes          |                            |
| 4. Multiple Anomalies| `temperature = 95.0°F`, `vibration = 0.8`                        | Flag both issues, log                            | ✅ `alerts/`      | ✅ Yes          | Message includes both reasons |
| 5. Edge Case         | `temperature = 90.0`, `vibration = 0.7` (on-threshold)           | Treated as normal (not anomaly)                  | ✅ `raw/` only    | ❌ No alert     | Thresholds are strictly greater than (>), not ≥   |
| 6. Malformed Payload | `temperature = "high"`, `vibration = null`, missing humidity     | Log as invalid, skip processing                  | ✅ `invalid/`     | ❌ No alert     | Validation fails, logged as error or written to `invalid/` |

---

## 🔎 Sample Inputs Directory

Located in: `test_inputs/`

| Filename                  | Description          |
|---------------------------|----------------------|
| `valid_payload.json`      | Normal sensor reading|
| `high_temp.json`          | Triggers temp alert  |
| `high_vibration.json`     | Triggers vibration alert |
| `multi_anomaly.json`      | Triggers both alerts |
| `edge_case_payload.json`  | Right at thresholds  |
| `malformed_payload.json`  | Missing or bad fields|

---

## ✅ Validation Checklist

- [ ] All test cases produce expected CloudWatch logs
- [ ] Alerts received for anomalies
- [ ] Files written to correct S3 bucket/prefix
- [ ] Invalid data is not processed further

---

## 📌 Notes

- Thresholds used: `temperature > 90.0°F`, `vibration > 0.7`
- Timestamps must follow ISO 8601 UTC format with `Z` suffix
- `device_id` must be unique per simulated rack