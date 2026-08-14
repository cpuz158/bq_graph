# Role & Objective
당신은 Google Cloud BigQuery Graph 및 시맨틱 온톨로지(Semantic Ontology) 전문 풀스택 엔지니어입니다.
**3대 비즈니스 도메인(🚗 자동차 / 🛍️ 이커머스 / 📱 모바일 요금제)** 지식 그래프를 바탕으로, 사용자 발화 의도(Intent)와 온톨로지 공리(Axioms & Constraints)에 따라 탐색 범위와 가중치가 동적으로 변경되는 **멀티 도메인 인터랙티브 Streamlit 웹 애플리케이션(`app.py`) 단일 파일**을 완성형으로 작성해 주세요.

---

## 1. 3대 비즈니스 도메인 지식 그래프 및 온톨로지 공리 정의

### 🚗 도메인 1: 자동차 (Automotive)
- **노드 구조 (5대 Entity Types)**:
  - `FamilyCar`: 패밀리카 차종 (`소렌토`, `싼타페`)
  - `ModelCode`: 세부 트림/파워트레인 (`MQ4`, `MQ4 HEV`, `MQ4a`, `MX5`, `MX5 HEV`, `MX5a`)
  - `Region`: 판매 지역 (`KR`, `US`, `SEA`)
  - `SpecItem`: 사양/옵션 (`1.6T HEV`, `2.5T 가솔린`, `전자식 AWD`, `HUD`, `드라이브 와이즈`, `빌트인 캠 2`, `선루프`)
  - `MarketingInfo`: 마케팅 소구점 (`2025 신형 출시 & 사전계약`, `동급 최고 실내공간`, `하이브리드 세제 혜택`, `스타맵 라이팅`)
- **관계(Edges)**: `BELONGS_TO`, `AVAILABLE_IN`, `APPLIES_SPEC`, `HAS_KSP`
- **온톨로지 공리**:
  - `[Constraint]` `ModelCode`는 1개의 `FamilyCar`에만 귀속.
  - `[Axiom]` `Region='KR'`인 내수 모델만 국내 사양 `SpecItem`과 유효한 `APPLIES_SPEC` 관계를 맺음.
- **발화 시나리오**:
  1. `"신형 소렌토 곧 나온다며?"` (Intent: `INFO_SEARCH` / `HAS_KSP` 최우선 가중치 0.1)
  2. `"소렌토 구매하려고 하는데 옵션 추천해줘"` (Intent: `PURCHASE_INTENT` / `APPLIES_SPEC` 최우선 가중치 0.1)

---

### 🛍️ 도메인 2: 이커머스 (E-Commerce)
- **노드 구조 (5대 Entity Types)**:
  - `BrandCategory`: 상위 브랜드/카테고리 (`나이키 러닝`, `프리미엄 캠핑 텐트`)
  - `ProductSKU`: 개별 상품 SKU (`에어 줌 페가수스 41`, `에어 줌 알파플라이 3`, `베이퍼플라이 3`, `어메니티 돔 텐트`, `랜드락 대형 쉘터`)
  - `TargetSegment`: 타깃 고객군 (`입문/초보 러너 & 캠퍼`, `마라톤 풀코스 & 헤비 캠퍼`)
  - `ProductSpec`: 상세 스펙/소재 (`ZoomX 초경량 폼`, `풀렝스 카본 플라이플레이트`, `ReactX 폼`, `내수압 3,000mm 립스탑`, `두랄루민 7001 폴대`)
  - `PromoEvent`: 기획전/프로모션 (`봄맞이 런페스타 20% 할인쿠폰`, `알파플라이 3 론칭 사은품 증정`, `아웃도어 페스타 그라운드시트 증정`)
- **관계(Edges)**: `BELONGS_TO`, `TARGETS`, `APPLIES_SPEC`, `HAS_PROMO`
- **온톨로지 공리**:
  - `[Constraint]` `ProductSKU`는 1개의 상위 `BrandCategory`에만 귀속.
  - `[Axiom]` 타깃 세그먼트가 '입문 러너'인 경우 레이싱 전용 고가 사양 제외.
- **발화 시나리오**:
  1. `"요즘 인기 있는 러닝화 기획전 있어?"` (Intent: `INFO_SEARCH` / `HAS_PROMO` 최우선 가중치 0.1)
  2. `"페가수스 41 쿠셔닝 폼이랑 무게 스펙 알려줘"` (Intent: `PURCHASE_INTENT` / `APPLIES_SPEC` 최우선 가중치 0.1)

---

### 📱 도메인 3: 모바일 요금제 (Telco)
- **노드 구조 (5대 Entity Types)**:
  - `PlanFamily`: 요금제 패밀리 (`5G 프리미어 패밀리`, `너겟 다이렉트`, `시니어 안심 케어`)
  - `PlanCode`: 세부 요금제 코드 (`5G 프리미어 슈퍼`, `5G 프리미어 플러스`, `너겟 5G 청년 무제한`, `5G 시니어 49`)
  - `TargetUser`: 가입 대상 고객군 (`일반 가입자`, `청년 고객군 (만 19~34세)`, `시니어 고객군 (만 65세 이상)`)
  - `PlanSpec`: 데이터/QoS 기본 스펙 (`기본 데이터 완전 무제한`, `테더링 50GB 전용 한도`, `QoS 5Mbps 안심 무제한`, `스마트기기 2회선 무료`)
  - `MarketingBenefit`: 부가 혜택/멤버십 (`넷플릭스/디즈니+ 구독팩 무료`, `VVIP 영화 연 12회 무료`, `가족 유무선 결합할인`, `보이스피싱 안심 보상 보험`)
- **관계(Edges)**: `BELONGS_TO`, `TARGETS`, `APPLIES_PLAN_SPEC`, `HAS_BENEFIT`
- **온톨로지 공리**:
  - `[Constraint]` `PlanCode`는 1개의 `PlanFamily`에만 귀속.
  - `[Axiom]` 연령 인증(청년/시니어) 통과 시에만 전용 요금제 및 특화 혜택 노드 연결.
- **발화 시나리오**:
  1. `"OTT 무료로 볼 수 있는 5G 요금제 뭐가 있어?"` (Intent: `INFO_SEARCH` / `HAS_BENEFIT` 최우선 가중치 0.1)
  2. `"5G 프리미어 슈퍼 테더링 한도랑 QoS 속도 얼마야?"` (Intent: `PURCHASE_INTENT` / `APPLIES_PLAN_SPEC` 최우선 가중치 0.1)

---

## 2. 10대 개발자 인기 IDE 테마 팔레트 (Light 4종 + Dark 6종)

사이드바에서 테마를 실시간 전환할 수 있으며, 전체 UI 배경, 사이드바, 카드, 텍스트, 그래프 캔버스 및 노드 배색이 일관되게 동기화됩니다:
- **☀️ Light Themes (4종)**: `VS Code Light+`, `GitHub Light`, `One Light (Atom)`, `Solarized Light`
- **🌙 Dark Themes (6종)**: `VS Code Dark+`, `Dracula`, `One Dark Pro`, `Monokai Pro`, `Nord`, `GitHub Dark Dimmed`

### [CSS 주입 및 구문 강조 핵심 규칙]
1. 일반 텍스트는 테마의 `text` 색상으로 강제 적용하되, 코드 블록 내부 Prism.js 토큰은 제외합니다:
   `.stApp span:not(pre span):not(code span):not([class*="token"]) { color: {text} !important; }`
2. `div[data-testid="stCodeBlock"] .token.keyword`, `.token.string`, `.token.comment` 등에 테마별 고유 구문 강조 색상을 주입하여 선명한 하이라이팅을 보장합니다.

---

## 3. UI/UX 레이아웃 구조 (Full-Width Top-Down Vertical Layout)

### A. 좌측 사이드바
1. **📂 비즈니스 도메인 선택기**: `🚗 자동차 (Automotive)`, `🛍️ 이커머스 (E-Commerce)`, `📱 모바일 요금제 (Telco)`
2. **🎨 IDE UI 테마 선택기**: Light 4종 + Dark 6종 전환.
3. **🗣️ 발화 시나리오 라디오**: 도메인별 프리셋 4종 + 직접 입력 (`key`를 도메인 ID와 결합하여 상태 충돌 방지).
4. **🎯 의도 추론 및 시작 노드**: `INFO_SEARCH` vs `PURCHASE_INTENT` 라디오 + 시작 노드 선택기.
5. **⚙️ 온톨로지 파라미터**: `Max Hop (1~3)`, `Edge Weight Threshold (0.0~1.0)`, 도메인별 필터 (Region / Segment / TargetUser).

### B. 메인 패널 (위/아래 수직 전폭 배치)

#### [헤더 및 상단 KPI 메트릭 & 가이드]
1. 도메인별 메인 타이틀 및 현재 의도/테마 상태 표시.
2. 온톨로지 가중치 탐색 원리 안내 카드.
3. 4대 KPI 메트릭 카드: `Active Subgraph Nodes`, `Active Traverse Edges`, `Query Execution Time (12.4ms)`, `Context Density Score (%)`.
4. **`💡 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드` Expander**: 도메인별 마케팅/프로모션 vs 기술/제원 스펙 비교 테이블.

#### [상단 영역] 🕸️ Interactive Knowledge Graph Visualization (Full Width, 710px)
1. **그래프 렌더링 엔진 선택 드롭다운**:
   - `1. PyVis (Vis.js 물리 시뮬레이션)`: `forceAtlas2Based` 물리 엔진, 마우스 휠 줌/팬, 노드 자유 드래그, 다크/라이트 배경 스트로크 폰트, 유니코드 카드형 텍스트 툴팁.
   - `2. Cytoscape.js (엔지니어링/구조적 레이아웃)`: COSE compound 레이아웃, 베지어 곡선 엣지, 마우스 호버 위치 추적 플로팅 툴팁(`div#cy-tooltip`).
2. 범례 배지 박스 (5대 노드 타입 배색 동기화).

#### [하단 영역] ⚡ Dynamic Cypher/GQL Query & Grounding Result (4-Tabs)
- **Tab 1: ⚡ Dynamic GQL Query**
  - 도메인별 BigQuery 표준 GQL 쿼리 (`GRAPH ... MATCH ... WHERE ... RETURN ... ORDER BY ...`) 대문자 포맷팅.
  - BigQuery GoogleSQL `GRAPH_TABLE` 멀티홉 탐색 쿼리.
  - openCypher 표준 쿼리 Expander.
  - 도메인 특화 서브그래프 기반 RAG 응답 시뮬레이션 (`st.info`) 및 LLM 주입 프롬프트 컨텍스트 JSON (`st.json`).
- **Tab 2: 📜 BigQuery Property Graph DDL**
  - Google Cloud BigQuery 공식 `CREATE OR REPLACE PROPERTY GRAPH` DDL 스크립트 (`NODE TABLES`, `EDGE TABLES`, `SOURCE KEY REFERENCES`, `DESTINATION KEY REFERENCES`).
  - DDL 구문 핵심 가이드 정보 콜아웃.
- **Tab 3: 🕸️ Filtered Subgraph**
  - 활성화된 노드 목록 테이블 (Node ID, Entity Name, Type, Hop Distance, Cost, Relevance).
  - 활성화된 엣지 목록 테이블 (Source Node, Relation, Target Node, Dynamic Weight, Description).
- **Tab 4: 🗄️ BigQuery Native Tables**
  - BigQuery Property Graph의 기반이 되는 물리적 원본 관계형 테이블(차종/SKU/요금제 마스터, 매핑 테이블) 조회 셀렉트박스.
  - 테이블별 `NODE TABLE` 또는 `EDGE TABLE` 매핑 안내 정보 콜아웃.

---

## 4. 기술 스택 및 실행 요구사항

- **Python 라이브러리**: `streamlit`, `pyvis`, `networkx`, `pandas`, `plotly`
- **구현 형태**: 외부 DB 연결 없이 즉시 `streamlit run app.py`로 구동 가능한 **단일 Python 파일 (`app.py`)** 완성형 코드.
- **오류 방지**: 위젯 `key`와 SessionState 동기화 콜백(`on_preset_change`, `on_domain_change`)으로 상태 반응성 100% 보장, 고대비 CSS 및 Prism.js 구문 강조 보존.
