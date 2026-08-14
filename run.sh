#!/usr/bin/env bash

# ==============================================================================
# BigQuery Knowledge Graph Explorer - 로컬 구동 스크립트 (run.sh)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "=================================================================="
echo "🚀 BigQuery Knowledge Graph Explorer 시작 중..."
echo "=================================================================="

# 1. 가상환경 확인 및 생성
if [ ! -d ".venv" ]; then
    echo "📦 Python 가상환경(.venv)이 존재하지 않아 새로 생성합니다..."
    python3 -m venv .venv
fi

# 2. 가상환경 활성화
echo "🔌 Python 가상환경 활성화..."
source .venv/bin/activate

# 3. 필수 패키지 설치 확인
echo "📥 의존성 패키지 확인 및 설치..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# 4. Streamlit 웹 앱 구동
PORT=${PORT:-8501}
ADDRESS=${ADDRESS:-"0.0.0.0"}

echo "------------------------------------------------------------------"
echo "🌐 로컬 서버 주소: http://localhost:${PORT}"
echo "🌐 네트워크 주소: http://${ADDRESS}:${PORT}"
echo "------------------------------------------------------------------"
echo "종료하려면 [Ctrl + C]를 누르세요."
echo "=================================================================="

exec streamlit run app.py \
    --server.port "${PORT}" \
    --server.address "${ADDRESS}" \
    --server.headless true \
    --browser.gatherUsageStats false
