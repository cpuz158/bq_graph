#!/usr/bin/env bash
set -e

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "hp-dragonfly")}
REGION=${REGION:-"asia-northeast3"}
SERVICE_NAME="vehicle-knowledge-graph"
REPO_NAME="cloud-run-source-deploy"

echo "=========================================="
echo "🚀 Deploying to Google Cloud Run"
echo "Project ID : ${PROJECT_ID}"
echo "Region     : ${REGION}"
echo "Service    : ${SERVICE_NAME}"
echo "=========================================="

# 1. 필수 Google Cloud API 활성화
echo "▶️ [1/3] Checking & enabling required Google Cloud APIs..."
gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com --project="${PROJECT_ID}"

# 2. Artifact Registry 리포지토리 확인 및 자동 생성 (gcr.io 지원 중단 대응)
echo "▶️ [2/3] Ensuring Artifact Registry repository exists..."
gcloud artifacts repositories describe "${REPO_NAME}" \
  --location="${REGION}" \
  --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud artifacts repositories create "${REPO_NAME}" \
  --repository-format=docker \
  --location="${REGION}" \
  --description="Cloud Run Docker Repository" \
  --project="${PROJECT_ID}"

IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:latest"

# 3. Cloud Build를 통한 컨테이너 빌드 및 Artifact Registry 푸시
echo "▶️ [3/3] Building and pushing container image to Artifact Registry..."
gcloud builds submit --tag "${IMAGE_NAME}" --project="${PROJECT_ID}"

# 4. Cloud Run 서비스 배포
echo "▶️ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project="${PROJECT_ID}" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1

echo "=========================================="
echo "✅ Deployment Successful!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --project="${PROJECT_ID}" --format="value(status.url)")
echo "🌐 Service URL: ${SERVICE_URL}"
echo "=========================================="
