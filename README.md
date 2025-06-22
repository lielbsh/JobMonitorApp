# Job Monitor - Automated Job Application Tracker

## 🎯 Project Overview

An automated system for tracking job application emails. It:

- Scans your **Gmail inbox**
- Identifies emails related to job applications, interviews, or rejections
- Automatically classifies them using **OpenAI API** or **regex** (for structured sources)
- Saves structured job and email data to an **RDS PostgreSQL** database

---

## 🛠️ Technologies Used

- **Python**
- **AWS Lambda** – Two Lambda functions:
  - `lambda_analyze_email` – scans and classifies emails
  - `lambda_db` – stores classified data in the database
- **Amazon EventBridge** – triggers the scanning Lambda every ~2 hours (during the day)
- **Amazon RDS** – PostgreSQL instance for persistent storage
- **Amazon S3** – stores timestamp file and `token.pickle`
- **OpenAI API** – for natural language classification of email content
- **Gmail API (OAuth2)** – secure email access
- **Regex** – fast classification of known formats (e.g., LinkedIn)
- **SQLite** – for optional local development mode

---

## ⚙️ System Flow

```
+-------------------+       +-------------------+       +------------------+
|   EventBridge     +------>+ lambda_analyze    +------>+  lambda_db       |
| (Scheduled every  |       |  - Gmail API      |       |  - Store jobs    |
|  ~2 hours)        |       |  - OpenAI / Regex |       |  - Track emails  |
+-------------------+       +-------------------+       +------------------+
```

1. Gmail messages are fetched with OAuth2.
2. Messages are filtered and classified.
3. Relevant data is passed to `lambda_db`.
4. Data is persisted in RDS.~
5. Processed timestamp is updated in S3.

---

## 🧩 Lambda Functions

### `lambda_analyze_email`

- Triggered by **EventBridge**
- Connects to Gmail using OAuth2
- Queries for relevant messages with smart filtering
- Extracts subject, body, and metadata
- Classifies the message using:
  - **Regex** (for LinkedIn emails)
  - **OpenAI API** (for free-text emails)
- If relevant → invokes `lambda_db`

### `lambda_db`

- Saves job and email data to **PostgreSQL**
- Smart logic to:
  - Create new job records
  - Update existing jobs
- One-to-many schema:
  - One job → many related emails (status updates, follow-ups)

---

## 💾 Storage

- **Amazon S3**:
  - `timestamp.json`: stores last processed timestamp
  - `token.pickle`: stores Gmail OAuth2 credentials
- **RDS PostgreSQL**:
  - Two tables with one-to-many relationship:
    - `jobs`
    - `emails`

---

## 🧪 Local Execution

- The project supports local execution with either:
  - Local SQLite
  - Remote PostgreSQL (RDS)
  - Running Lambdas locally via `scripts/scheduler.py`
- You can inject credentials locally and run the full pipeline end-to-end

---

## 🗂️ First-Time Setup

### 1. Set up Gmail API

- Create a project in [Google Cloud Console](https://console.cloud.google.com/)
- Enable Gmail API
- Download `credentials.json`

### 2. Set up OpenAI

```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 3. Install requirements

```bash
pip install -r requirements.txt
```

### 4. For local run (with SQLite)

```bash
python scripts/scheduler.py
```

- Runs the pipeline every 1 minute.
- Uses SQLite: `sqlite:///./JobMonitorApp.db`

For manual run:

```bash
python injection.py run
```

- Runs messages from the past 24 hours or `'bootstrap'` mode (2 months back) by default.

### 5. For AWS deployment

```bash
python scripts/init_token.py
```

```bash
python scripts/build_lambda_zip.py
```

- Builds Lambda ZIPs using Docker with all dependencies

You will need to:

- Upload to AWS Lambda manually or via Terraform/CDK
- Set up IAM roles with permissions:
  - `AmazonS3FullAccess` (or restricted bucket policy)
  - `AmazonRDSDataFullAccess`
  - `SecretsManagerReadWrite`
  - `CloudWatchLogsFullAccess`
  - Custom trust policies for Lambda invocation

---
