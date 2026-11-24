#!/usr/bin/env bash
set -eo pipefail

echo "=========================================================="
echo "ChronicleAI Docker End-to-End Smoke Test"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

cleanup() {
  local exit_code=$?
  echo "Tearing down containers..."
  docker compose logs > docker_smoke_test.log 2>&1 || true
  docker compose down -v || true
  if [ $exit_code -ne 0 ]; then
    echo "❌ Docker Smoke Test FAILED (Exit Code: $exit_code)"
    echo "Recent Docker logs:"
    tail -n 60 docker_smoke_test.log || true
  else
    echo "✅ Docker Smoke Test PASSED successfully"
    rm -f docker_smoke_test.log
  fi
  exit $exit_code
}

trap cleanup EXIT

echo "1. Building and launching Docker Compose stack..."
docker compose up --build -d

echo "2. Waiting for backend healthcheck to report healthy..."
MAX_RETRIES=30
RETRY_COUNT=0
HEALTHY=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  STATUS=$(docker inspect --format='{{json .State.Health.Status}}' chronicle_backend 2>/dev/null || echo "\"unknown\"")
  if [ "$STATUS" = "\"healthy\"" ]; then
    HEALTHY=1
    echo "   Backend reported healthy after $((RETRY_COUNT * 2))s."
    break
  fi
  RETRY_COUNT=$((RETRY_COUNT + 1))
  sleep 2
done

if [ $HEALTHY -ne 1 ]; then
  echo "❌ Backend container failed to become healthy within 60s."
  docker compose ps
  exit 1
fi

echo "3. Testing Backend Health API..."
HEALTH_RESP=$(curl -s -f http://localhost:8000/api/health)
echo "   /api/health response: ${HEALTH_RESP}"
echo "${HEALTH_RESP}" | grep -q '"status":"healthy"'

echo "4. Testing Frontend HTTP response..."
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
echo "   Frontend root HTTP status: ${FRONTEND_CODE}"
if [ "$FRONTEND_CODE" -ne 200 ]; then
  echo "❌ Expected frontend status 200, got ${FRONTEND_CODE}"
  exit 1
fi

echo "5. Testing Document Listing API..."
DOCS_RESP=$(curl -s -f http://localhost:8000/api/documents)
echo "${DOCS_RESP}" | grep -q "le_thanh_tong"
echo "   Documents verified: $(echo "${DOCS_RESP}" | grep -o '"filename":' | wc -l) documents listed."

echo "6. Testing RAG Search API..."
SEARCH_RESP=$(curl -s -f -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Luật Hồng Đức phụ nữ", "top_k": 3}')
echo "${SEARCH_RESP}" | grep -q '"results":'
echo "   RAG search returned results successfully."

echo "7. Testing Claim Verification API..."
VERIFY_RESP=$(curl -s -f -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"claims": ["Năm 1460, Hoàng đế Lê Thánh Tông lên ngôi ở tuổi 18."]}')
echo "${VERIFY_RESP}" | grep -q '"SUPPORTED"'
echo "   Claim verification returned SUPPORTED status."

echo "8. Testing Script Generation API..."
SCRIPT_RESP=$(curl -s -f -X POST http://localhost:8000/api/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{"subject": "Hoàng đế Lê Thánh Tông", "format": "SHORTS"}')
echo "${SCRIPT_RESP}" | grep -q '"scenes":'
echo "   Script generated with verified scenes."

echo "9. Testing Video Production API (Fast Scene Render)..."
VIDEO_RESP=$(curl -s -f -X POST http://localhost:8000/api/videos/render \
  -H "Content-Type: application/json" \
  -d '{"subject": "Hoàng đế Lê Thánh Tông", "format": "SHORTS", "aspect_ratio": "16:9"}')
echo "${VIDEO_RESP}" | grep -q '"completed"'
echo "   Video production completed successfully."

echo "10. Testing Video Stream and Download Endpoints..."
curl -s -f -I http://localhost:8000/api/videos/latest | grep -q "200"
curl -s -f -I http://localhost:8000/api/videos/latest | grep -q "completed"
echo "   Latest video verified and ready for streaming/download."

echo "=========================================================="
echo "All Docker End-to-End Smoke Tests Passed!"
echo "=========================================================="
