# TikTok Safety Platform — Quick Start (Streaming Only)

## Mô tả ngắn

Dự án triển khai pipeline dữ liệu lớn để phát hiện nội dung độc hại trên TikTok theo thời gian thực. Hệ thống thu thập link video, tải video về MinIO, gửi metadata vào Kafka và dùng Spark Structured Streaming để suy luận bằng mô hình AI, sau đó lưu kết quả vào PostgreSQL và hiển thị trên Dashboard Streamlit.

## Chức năng chính

Hệ thống cung cấp luồng xử lý thời gian thực, suy luận đa phương thức, dashboard giám sát, và cơ chế tự động điều phối bằng Airflow. Pipeline ưu tiên chế độ fusion nếu tải được model, nếu không sẽ tự động fallback sang late-score.

## Yêu cầu tối thiểu

| Thành phần | Tối thiểu | Khuyến nghị |
|---|---|---|
| OS | Ubuntu 20.04+ / Windows 10+ (WSL2) | Ubuntu 22.04 |
| Docker | 20.10+ & Compose v2 | Bản mới nhất |
| Python | 3.9+ | 3.10+ |
| RAM | 16GB | 32GB |
| Dung lượng | 50GB | 100GB+ |

## Cây thư mục (tóm lược đầy đủ các phần chính)

```
UIT-SE363-Big-Data-Platform-Application-Development/
├── README.md
├── README_START.md
├── REPORT.md
├── requirements.txt
├── streaming/
│   ├── docker-compose.yml
│   ├── start_all.sh
│   ├── .env.example
│   ├── airflow/
│   ├── ingestion/
│   ├── processing/
│   ├── dashboard/
│   ├── mlflow/
│   ├── infra/
│   ├── scripts/
│   └── tests/
├── train_eval_module/
│   ├── text/
│   ├── video/
│   ├── fusion/
│   ├── audio/
│   ├── configs/
│   ├── data_splits/
│   ├── scripts/
│   └── shared_utils/
├── crawl_scripts/
├── notebooks/
├── processed_data/
├── data/
├── data_1/
├── data_viet/
└── docs/
```

## Clone repository

Cách 1 (HTTPS):

```
git clone https://github.com/BinhAnndapoet/UIT-SE363-Big-Data-Platform-Application-Development.git
cd UIT-SE363-Big-Data-Platform-Application-Development
```

Cách 2 (SSH):

```
git clone git@github.com:BinhAnndapoet/UIT-SE363-Big-Data-Platform-Application-Development.git
cd UIT-SE363-Big-Data-Platform-Application-Development
```

## Tạo môi trường ảo và cài package

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Chuẩn bị cookies cho crawler

Cần có `cookies.txt` lấy từ trình duyệt đã đăng nhập TikTok. Lưu file vào:

```
streaming/ingestion/cookies.txt
```

## Tải dữ liệu từ Google Drive và đặt đúng folder

| Folder | Link | Mô tả |
|--------|------|-------|
| `data/` | [Google Drive](https://drive.google.com/drive/folders/1rfEyJnUaM8p0s4deP9GoSV0RMwxY62Lu?usp=sharing) | Mixed EN+VI hashtags (batch 1) |
| `data_1/` | [Google Drive](https://drive.google.com/drive/folders/1yVywtRKArInyWX4hZ5q00FjG4jgJ8kZE?usp=sharing) | Mixed EN+VI hashtags (batch 2) |
| `data_viet/` | [Google Drive](https://drive.google.com/drive/folders/1W6OBCbU_e3_Rsp3QYNV5f3ozWi8KVn4v?usp=sharing) | Vietnamese-only hashtags |

Tải và giải nén vào root của dự án. Sau khi tải, đảm bảo cấu trúc như sau:

```
UIT-SE363-Big-Data-Platform-Application-Development/
├── data/
├── data_1/
├── data_viet/
├── processed_data/
```

Nếu Google Drive cung cấp file nén, giải nén và đặt trực tiếp các thư mục trên vào root. Không đặt lồng thêm một thư mục trung gian.

## Chạy streaming pipeline (Docker Compose)

1. Sao chép file môi trường và cấu hình nếu cần.

```
cp streaming/.env.example streaming/.env
```

2. Khởi chạy hệ thống bằng Docker Compose.

```
cd streaming
docker compose up -d --build
```

3. Kiểm tra trạng thái và xem log nếu cần.

```
docker compose ps
docker compose logs -f spark-processor
```

4. Mở Airflow tại http://localhost:8089 (tài khoản mặc định admin/admin) và chạy lần lượt:

- DAG `1_TIKTOK_ETL_COLLECTOR` (crawl link TikTok)
- DAG `2_TIKTOK_STREAMING_PIPELINE` (ingestion + Spark streaming)
- DAG `3_MODEL_RETRAINING` (tuỳ chọn, retraining định kỳ)

5. Mở Dashboard tại http://localhost:8501 để quan sát kết quả.

6. Khi cần dừng hệ thống:

```
docker compose down
```

## Các port dịch vụ để kiểm tra nhanh

| Dịch vụ | URL | Ghi chú |
|---|---|---|
| Dashboard | http://localhost:8501 | Theo dõi realtime |
| Airflow | http://localhost:8089 | admin / admin |
| Spark Master UI | http://localhost:9090 | Quản trị Spark |
| MLflow | http://localhost:5000 | Tracking & registry |
| MinIO Console | http://localhost:9001 | admin / password123 |
| MinIO API | http://localhost:9000 | S3-compatible |
| Kafka | localhost:9092 | Broker |
| PostgreSQL | localhost:5432 | user / password (xem .env) |

## Lệnh Docker bổ sung (tùy chọn)

```
docker compose up -d --build
docker compose ps
docker compose logs -f spark-processor
docker compose down
```

## Kiểm tra nhanh kết quả

Sau khi DAG 2 chạy, bảng `processed_results` trong PostgreSQL sẽ có dữ liệu. Có thể kiểm tra qua Dashboard hoặc dùng test scripts trong `streaming/tests/`, ví dụ:

```
cd streaming
./tests/test_layer3_processing.sh
./tests/test_layer4_dashboard.sh
```

## Troubleshooting nhanh

Nếu Spark chưa xử lý dữ liệu, kiểm tra log của `spark-processor` và trạng thái Kafka. Nếu Airflow không chạy DAG, kiểm tra scheduler/webserver và kết nối Postgres. Có thể reset toàn bộ bằng cách dừng các container và xóa state nếu cần.

## Ghi chú

Tài liệu này chỉ tập trung vào chạy pipeline streaming. Hướng dẫn train model nằm trong `train_eval_module/README.md` và không yêu cầu khi demo streaming.
