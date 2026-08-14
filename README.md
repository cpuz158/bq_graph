# 🌐 Google Cloud BigQuery Graph Multi-Domain Semantic Subgraph Explorer

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Cloud BigQuery](https://img.shields.io/badge/Google%20Cloud-BigQuery%20Graph%20(GQL)-4285F4.svg?logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Google Cloud BigQuery Graph (GQL)** 및 **시맨틱 온톨로지(Semantic Ontology)** 기반의 **3대 비즈니스 도메인(🚗 자동차 / 🛍️ 이커머스 / 📱 모바일 요금제)** 지식 그래프 탐색 및 LLM 컨텍스트 그라운딩 시뮬레이터입니다.

사용자의 발화 의도(`INFO_SEARCH` vs `PURCHASE_INTENT`)와 비즈니스 공리(Axioms & Constraints)에 따라 최적의 지식 서브그래프를 실시간으로 탐색하고, BigQuery GQL 표준 쿼리 생성 및 RAG 컨텍스트 주입 결과를 시각화합니다.

---

## 🌟 3대 비즈니스 도메인 (Business Domains)

| 도메인 | 상위 엔티티 (Parent) | 하위 SKU/코드 (Child) | 마케팅/혜택 (Marketing) | 기술/제원 스펙 (Spec) | 필터 기준 (Filter) |
|---|---|---|---|---|---|
| **🚗 자동차 (Automotive)** | `FamilyCar` (소렌토, 싼타페) | `ModelCode` (MQ4, MX5 등) | `MarketingInfo` (신차출시, 공간성) | `SpecItem` (1.6T HEV, AWD, HUD) | 판매지역 (`KR`, `US`, `SEA`) |
| **🛍️ 이커머스 (E-Commerce)** | `BrandCategory` (나이키 러닝, 텐트) | `ProductSKU` (페가수스, 알파플라이) | `PromoEvent` (20% 쿠폰, 사은품) | `ProductSpec` (ZoomX, 카본플레이트) | 고객 세그먼트 (`입문`, `마라톤`) |
| **📱 모바일 요금제 (Telco)** | `PlanFamily` (5G 프리미어, 너겟) | `PlanCode` (슈퍼, 청년무제한) | `MarketingBenefit` (OTT 무료, VIP) | `PlanSpec` (무제한, 테더링 50G, QoS) | 가입 대상 (`일반`, `청년`, `시니어`) |

---

## 🚀 주요 기능 (Key Features)

### 1. 🕸️ 듀얼 그래프 렌더링 엔진 (Dual Graph Visualization)
- **PyVis (Vis.js Physics)**: `forceAtlas2Based` 물리 시뮬레이션으로 노드가 자연스럽게 퍼지며 자유로운 드래그, 줌, 팬 인터랙션 제공.
- **Cytoscape.js (COSE Layout)**: 생물정보학/네트워크 공학 표준 계층 레이아웃 및 베지어 곡선(Bezier Curve) 엣지 제공.
- **마우스 호버 카드 툴팁**: 노드 및 엣지에 마우스를 올리면 상세 메타데이터와 가중치 정보가 카드 형태로 렌더링.

### 2. 🎨 10대 개발자 인기 IDE 테마 실시간 전환
사이드바에서 라이트/다크 테마를 실시간으로 전환할 수 있으며, 전체 UI 배경, 카드, 텍스트, 그래프 캔버스 및 노드 배색이 일관되게 동기화됩니다:
- **☀️ Light Themes (4종)**: `VS Code Light+`, `GitHub Light`, `One Light (Atom)`, `Solarized Light`
- **🌙 Dark Themes (6종)**: `VS Code Dark+`, `Dracula`, `One Dark Pro`, `Monokai Pro`, `Nord`, `GitHub Dark Dimmed`

### 3. ⚡ BigQuery GQL 쿼리 생성 & 구문 강조 (Syntax Highlighting)
- 표준 **BigQuery GQL (`GRAPH ... MATCH ... WHERE ... RETURN`)** 및 **GoogleSQL `GRAPH_TABLE`** 멀티홉 탐색 쿼리를 동적 생성.
- Prism.js 기반 키워드, 함수, 엔티티 구문 강조 최적화 적용 (`language="sql"`).

### 4. 🤖 LLM Grounding Context & 응답 시뮬레이션
- 탐색된 서브그래프를 JSON 페이로드 구조로 가공하여 LLM 프롬프트 주입 컨텍스트로 전달.
- 도메인별 의도에 맞춘 RAG 응답 생성 시뮬레이션.

### 5. 🗄️ BigQuery Native 원본 테이블 & 서브그래프 상호 비교
- BigQuery Property Graph(`CREATE PROPERTY GRAPH`)의 기반이 되는 물리적 원본 관계형 테이블(차종/SKU/요금제 마스터, 매핑 테이블)을 즉시 열람하고, `NODE TABLE` 및 `EDGE TABLE` 매핑 관계를 직관적으로 비교.

---

## 🚀 로컬 실행 방법 (Local Getting Started)

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/vehicle-knowledge-graph.git
cd vehicle-knowledge-graph

# 2. Python 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 필수 패키지 설치
pip install -r requirements.txt

# 4. Streamlit 앱 실행
streamlit run app.py
```
브라우저에서 `http://localhost:8501`로 접속하여 도메인 및 테마를 자유롭게 전환하며 테스트할 수 있습니다.

---

## ☁️ Google Cloud Run 배포 가이드 (Deployment)

```bash
# GCP 프로젝트 ID 설정 후 배포 스크립트 실행
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-northeast3"  # 서울 리전

./deploy.sh
```

---

## 📂 프로젝트 구조 (Repository Structure)

```
.
├── app.py              # Streamlit 단일 구동 메인 애플리케이션 (3대 도메인, 10대 테마, 듀얼 렌더러)
├── requirements.txt    # Python 의존성 패키지 목록
├── Dockerfile          # Cloud Run 컨테이너 빌드 파일
├── deploy.sh           # Google Cloud Run 원클릭 배포 스크립트
├── .gitignore          # Git 제외 설정 (.venv, 캐시, HTML 등)
├── AGENT.md            # 시스템 아키텍처 및 3대 도메인 온톨로지 요구사항 명세
└── README.md           # 프로젝트 문서 및 사용 가이드
```

---

## 📄 라이선스 (License)
This project is licensed under the [MIT License](LICENSE).
