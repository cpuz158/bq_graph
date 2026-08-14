#!/usr/bin/env bash
set -e

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "your-gcp-project-id")}
REGION=${REGION:-"asia-northeast3"}
SERVICE_NAME="vehicle-knowledge-graph"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "=========================================="
echo "🚀 Deploying to Google Cloud Run"
echo "Project ID : ${PROJECT_ID}"
echo "Region     : ${REGION}"
echo "Service    : ${SERVICE_NAME}"
echo "=========================================="

# Build container image with Cloud Build
gcloud builds submit --tag "${IMAGE_NAME}"

# Deploy to Cloud Run
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1

echo "=========================================="
echo "✅ Deployment Successful!"
gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format="value(status.url)"
echo "=========================================="
