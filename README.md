# 🛡️ TikTok Safety Platform - Big Data Harmful Content Detection System

<div align="center">

**📚 Course**: SE363 - Big Data Platform Application Development  
**🏛️ Institution**: University of Information Technology (UIT) - VNU-HCM  
**👥 Authors**: [KhoiBui16](https://github.com/KhoiBui16) • [BinhAnndapoet](https://github.com/BinhAnndapoet) • [PhamQuocNam](https://github.com/PhamQuocNam)

---

![TikTok Safety](https://img.shields.io/badge/TikTok-Safety-ff0050?style=for-the-badge&logo=tiktok&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache-Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache-Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)

**A Big Data platform for detecting harmful content on TikTok using multimodal AI (Text + Video + Fusion)**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Models](#-ai-models) • [API Reference](#-api-reference)

</div>

---

## 📋 Project Overview

This project implements a **Lambda Architecture** based Big Data platform for real-time detection of harmful content on TikTok videos. The system combines:

- **Batch Processing**: Training multimodal AI models (Text, Video, Fusion)
- **Stream Processing**: Real-time video analysis using Apache Spark Streaming
- **Serving Layer**: Streamlit Dashboard for monitoring and content moderation

### Key Capabilities

- 🔍 **Multimodal Analysis**: Combines text (captions, comments) and video frame analysis
- ⚡ **Real-time Processing**: Stream processing with Kafka + Spark
- 🤖 **AI-Powered Detection**: State-of-the-art models for content classification
- 📊 **Interactive Dashboard**: Real-time monitoring and content audit tools
- 🔄 **MLflow Integration**: Model versioning and auto-update capabilities

---

## ✨ Features

### 1. Analytics Dashboard
- **KPI Monitoring**: Total processed videos, harmful detection rate, average risk score
- **Visual Analysis**: Time-series charts and category distribution
- **Real-time Updates**: Live data refresh from PostgreSQL

### 2. System Operations
- **Pipeline Control**: Start/Stop crawler and streaming pipelines
- **Status Monitor**: Real-time container and service health checks
- **System Logs**: Centralized logging viewer
- **Quick Actions**: One-click access to Airflow, MinIO, and queue management

### 3. Content Audit
- **Gallery Mode**: Visual grid of processed videos with risk scores
- **Detail View**: In-depth analysis of individual videos
- **Table View**: Sortable/filterable data table
- **Filters**: Category, score range, and keyword search

### 4. Database Manager
- **Table Browser**: Schema inspection and data preview
- **Query Tool**: Execute custom SQL queries
- **Statistics**: Database performance metrics
- **Maintenance**: Database optimization tools

### 5. Project Info
- **Architecture Diagrams**: Visual system documentation
- **Data Pipeline Flow**: End-to-end data journey
- **AI Models Documentation**: Model specifications and usage
- **Technical Documentation**: Detailed implementation guides

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAMBDA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │   TikTok     │───▶│   Crawler    │───▶│   MinIO (Storage)    │   │
│  │   Videos     │    │   Service    │    │   Videos & Audios    │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
│                             │                        │               │
│                             ▼                        ▼               │
│                      ┌──────────────┐    ┌──────────────────────┐   │
│                      │    Kafka     │───▶│   Spark Streaming    │   │
│                      │   Broker     │    │   (AI Inference)     │   │
│                      └──────────────┘    └──────────────────────┘   │
│                                                      │               │
│                                                      ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │   Streamlit  │◀───│  PostgreSQL  │◀───│   Processed Results  │   │
│  │   Dashboard  │    │   Database   │    │                      │   │
│  └──────────────┘    └──────────────┘    └──────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Services (Docker Compose)

| Service | Port | Description |
|---------|------|-------------|
| **Dashboard** | `8501` | Streamlit monitoring UI |
| **Airflow** | `8080` | DAG scheduling & orchestration |
| **Spark Master** | `9090` | Spark cluster management |
| **Spark Processor** | - | AI inference streaming job |
| **Kafka** | `9092` | Message broker |
| **MinIO** | `9000`, `9001` | Object storage (videos/audios) |
| **PostgreSQL** | `5432` | Results database |
| **MLflow** | `5000` | Model registry & tracking |

---

## 🤖 AI Models

All models are available on HuggingFace Hub:

### Text Classification Model
**Repository**: [KhoiBui/tiktok-text-safety-classifier](https://huggingface.co/KhoiBui/tiktok-text-safety-classifier)

- **Base Model**: CafeBERT (uitnlp/CafeBERT)
- **Task**: Binary classification (safe/harmful)
- **Input**: Video captions, comments, hashtags
- **Languages**: Vietnamese, English

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("KhoiBui/tiktok-text-safety-classifier")
model = AutoModelForSequenceClassification.from_pretrained("KhoiBui/tiktok-text-safety-classifier")

text = "your text here"
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
outputs = model(**inputs)
prediction = outputs.logits.argmax(-1).item()  # 0=safe, 1=harmful
```

### Video Classification Model
**Repository**: [KhoiBui/tiktok-video-safety-classifier](https://huggingface.co/KhoiBui/tiktok-video-safety-classifier)

- **Base Model**: VideoMAE (MCG-NJU/videomae-base-finetuned-kinetics)
- **Task**: Binary classification (safe/harmful)
- **Input**: 16 video frames (224x224)

```python
from transformers import AutoImageProcessor, VideoMAEForVideoClassification
from decord import VideoReader, cpu
import numpy as np

processor = AutoImageProcessor.from_pretrained("KhoiBui/tiktok-video-safety-classifier")
model = VideoMAEForVideoClassification.from_pretrained("KhoiBui/tiktok-video-safety-classifier")

# Load video and sample 16 frames
vr = VideoReader("video.mp4", ctx=cpu(0))
indices = np.linspace(0, len(vr) - 1, 16).astype(int)
frames = list(vr.get_batch(indices).asnumpy())

inputs = processor(frames, return_tensors="pt")
outputs = model(**inputs)
prediction = outputs.logits.argmax(-1).item()  # 0=safe, 1=harmful
```

### Multimodal Fusion Model
**Repository**: [KhoiBui/tiktok-multimodal-fusion-classifier](https://huggingface.co/KhoiBui/tiktok-multimodal-fusion-classifier)

- **Architecture**: Late Fusion with Cross-Attention
- **Text Backbone**: XLM-RoBERTa-base
- **Video Backbone**: VideoMAE-base
- **Fusion**: Cross-Attention + Gating Mechanism

---

## 📦 Installation

### Prerequisites

- **OS**: Ubuntu 20.04+ (recommended) or Windows 10+ with WSL2
- **Docker**: Docker Engine 20.10+ & Docker Compose v2
- **Python**: 3.9+
- **GPU**: NVIDIA GPU with CUDA 11.8+ (optional, for training)
- **RAM**: Minimum 16GB (32GB recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/BinhAnndapoet/UIT-SE363-Big-Data-Platform-Application-Development.git
cd UIT-SE363-Big-Data-Platform-Application-Development
```

### Step 2: Create Virtual Environment

**Ubuntu/Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp streaming/.env.example streaming/.env

# Edit as needed (default values work for development)
nano streaming/.env
```

**Key environment variables:**
```env
# PostgreSQL
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=tiktok_safety_db

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password123

# Airflow
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin

# HuggingFace Hub (optional - for loading models from Hub)
HF_MODEL_TEXT=KhoiBui/tiktok-text-safety-classifier
HF_MODEL_VIDEO=KhoiBui/tiktok-video-safety-classifier
HF_MODEL_FUSION=KhoiBui/tiktok-multimodal-fusion-classifier
HF_TOKEN=your_huggingface_token
```

---

## 🚀 Usage

### Quick Start (Ubuntu)

The easiest way to start all services:

```bash
cd streaming
chmod +x start_all.sh
./start_all.sh
```

This script will:
1. Clean up existing containers
2. Set proper file permissions
3. Build and start all Docker services
4. Configure Airflow connections
5. Initialize MinIO buckets

### Manual Docker Compose

```bash
cd streaming

# Start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f spark-processor
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8501 | - |
| **Airflow** | http://localhost:8080 | admin / admin |
| **MinIO Console** | http://localhost:9001 | admin / password123 |
| **Spark Master** | http://localhost:9090 | - |
| **MLflow** | http://localhost:5000 | - |

### Running the Pipeline

1. **Open Airflow** at http://localhost:8080
2. **Trigger DAG 1**: `1_TIKTOK_ETL_COLLECTOR` - Crawls TikTok videos
3. **Wait for completion** (Success status)
4. **Trigger DAG 2**: `2_TIKTOK_STREAMING_PIPELINE` - Starts streaming processing
5. **Monitor Dashboard** at http://localhost:8501

---

## 📁 Project Structure

| Path | Description |
|------|-------------|
| [streaming/](streaming/) | Streaming pipeline |
| [streaming/airflow/dags/](streaming/airflow/dags/) | Airflow DAG definitions |
| [streaming/dashboard/app.py](streaming/dashboard/app.py) | Main dashboard entry point |
| [streaming/dashboard/page_modules/](streaming/dashboard/page_modules/) | Dashboard page components |
| [streaming/ingestion/crawler.py](streaming/ingestion/crawler.py) | TikTok video crawler |
| [streaming/ingestion/downloader.py](streaming/ingestion/downloader.py) | Video downloader |
| [streaming/ingestion/clients/](streaming/ingestion/clients/) | MinIO, Kafka clients |
| [streaming/processing/spark_processor.py](streaming/processing/spark_processor.py) | Spark Streaming job (AI inference) |
| [streaming/mlflow/client.py](streaming/mlflow/client.py) | MLflow model registry client |
| [streaming/mlflow/model_updater.py](streaming/mlflow/model_updater.py) | Model auto-update mechanism |
| [streaming/docker-compose.yml](streaming/docker-compose.yml) | Main Docker Compose file |
| [streaming/start_all.sh](streaming/start_all.sh) | Full startup script |
| [streaming/tests/](streaming/tests/) | Test files |
| | |
| [train_eval_module/](train_eval_module/) | Model training and evaluation |
| [train_eval_module/text/](train_eval_module/text/) | Text classification model |
| [train_eval_module/video/](train_eval_module/video/) | Video classification model |
| [train_eval_module/fusion/](train_eval_module/fusion/) | Multimodal fusion model |
| [train_eval_module/scripts/push_hf_model.py](train_eval_module/scripts/push_hf_model.py) | Push models to HuggingFace Hub |
| [train_eval_module/shared_utils/](train_eval_module/shared_utils/) | Common utilities |
| | |
| [docs/](docs/) | Documentation |
| [docs/streaming/](docs/streaming/) | Streaming documentation |
| [docs/mlflow/MLFLOW_INTEGRATION_GUIDE.md](docs/mlflow/MLFLOW_INTEGRATION_GUIDE.md) | MLflow setup and usage |

---

## 🧪 Testing

### Automation Scripts (Ubuntu)

```bash
cd streaming

# Run all tests
./tests/run_all_tests.sh

# Test individual layers
./tests/test_layer1_infrastructure.sh  # Docker, network, services
./tests/test_layer2_ingestion.sh       # Crawler, MinIO, Kafka
./tests/test_layer3_processing.sh      # Spark, AI inference
./tests/test_layer4_dashboard.sh       # Dashboard UI tests
```

### Python Tests

```bash
cd streaming

# Run pytest
pytest tests/ -v

# Specific test files
pytest tests/test_dashboard.py -v
pytest tests/test_ingestion_layer.py -v
pytest tests/test_spark_layer.py -v
pytest tests/test_mlflow.py -v
```

### Test Files Overview

| File | Purpose |
|------|---------|
| `test_dashboard.py` | Dashboard UI and API tests |
| `test_db_layer.py` | PostgreSQL database tests |
| `test_ingestion_layer.py` | Crawler and ingestion tests |
| `test_spark_layer.py` | Spark processing tests |
| `test_mlflow.py` | MLflow integration tests |
| `test_comprehensive.sh` | Full end-to-end test |

---

## 📖 Documentation

Detailed documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| `docs/streaming/01_PROJECT_OVERVIEW.md` | Project introduction |
| `docs/streaming/02_LAYER_ARCHITECTURE.md` | Architecture details |
| `docs/streaming/03_DASHBOARD_PAGES.md` | Dashboard usage guide |
| `docs/streaming/04_SETUP_GUIDE.md` | Installation guide |
| `docs/streaming/05_TESTING_GUIDE.md` | Testing documentation |
| `docs/streaming/06_API_REFERENCE.md` | API documentation |
| `docs/mlflow/MLFLOW_INTEGRATION_GUIDE.md` | MLflow setup and usage |

---

## 🔧 Troubleshooting

### Common Issues

**1. Docker containers not starting:**
```bash
# Check container logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>
```

**2. Spark processor failing:**
```bash
# Check Spark logs
docker logs spark-processor -f

# Common fix: increase memory
# Edit docker-compose.yml: SPARK_WORKER_MEMORY=16g
```

**3. Database connection issues:**
```bash
# Verify PostgreSQL is healthy
docker exec postgres pg_isready -U user -d tiktok_safety_db
```

**4. Reset everything:**
```bash
cd streaming
docker compose down -v
rm -rf state/
./start_all.sh
```

---

## 👥 Authors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/KhoiBui16">
        <img src="https://github.com/KhoiBui16.png" width="100px;" alt="KhoiBui16"/><br />
        <sub><b>KhoiBui16</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/BinhAnndapoet">
        <img src="https://github.com/BinhAnndapoet.png" width="100px;" alt="BinhAnndapoet"/><br />
        <sub><b>BinhAnndapoet</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/PhamQuocNam">
        <img src="https://github.com/PhamQuocNam.png" width="100px;" alt="PhamQuocNam"/><br />
        <sub><b>PhamQuocNam</b></sub>
      </a>
    </td>
  </tr>
</table>

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Star this repo if you find it helpful! ⭐**

Made with ❤️ by KhoiBui16, BinhAnndapoet & PhamQuocNam

</div>
