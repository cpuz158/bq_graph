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

# 4. 포트 및 CLI 옵션 파싱
PORT=${PORT:-8501}
ADDRESS=${ADDRESS:-"0.0.0.0"}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -a|--address)
            ADDRESS="$2"
            shift 2
            ;;
        -h|--help)
            echo "사용법: ./run.sh [포트번호 또는 옵션]"
            echo ""
            echo "옵션:"
            echo "  -p, --port <포트번호>     Streamlit 포트 번호 지정 (기본값: 8501)"
            echo "  -a, --address <IP주소>    Streamlit 바인딩 주소 지정 (기본값: 0.0.0.0)"
            echo "  -h, --help               도움말 출력"
            echo ""
            echo "예시:"
            echo "  ./run.sh 8080"
            echo "  ./run.sh -p 9000"
            echo "  ./run.sh --port 8888"
            exit 0
            ;;
        *)
            if [[ "$1" =~ ^[0-9]+$ ]]; then
                PORT="$1"
                shift
            else
                echo "⚠️ 알 수 없는 옵션: $1 (도움말: ./run.sh --help)"
                shift
            fi
            ;;
    esac
done

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
