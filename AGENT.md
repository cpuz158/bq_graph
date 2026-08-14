# Role & Objective
당신은 Google Cloud BigQuery Graph 및 시맨틱 온톨로지(Semantic Ontology) 전문 풀스택 엔지니어입니다.
차량 도메인 지식 그래프(Vehicle Knowledge Graph)를 바탕으로, 사용자 발화 의도(Intent)와 온톨로지 공리(Axioms & Constraints)에 따라 탐색 범위와 가중치가 동적으로 변경되는 **인터랙티브 Streamlit 웹 애플리케이션(`app.py`) 단일 파일**을 완성형으로 작성해 주세요.

---

## 1. 지식 그래프 도메인 및 온톨로지 공리 정의

### A. 노드 스키마 (5대 Entity Types & Mock Data)
1. **`FamilyCar` (패밀리카 차종)**: `소렌토 (FC_SORENTO)`, `싼타페 (FC_SANTAFE)`
2. **`ModelCode` (세부 트림/파워트레인)**:
   - 소렌토: `MQ4 (내수 가솔린/디젤)`, `MQ4 HEV (내수 하이브리드)`, `MQ4a (북미 수출형)`
   - 싼타페: `MX5 (내수 가솔린)`, `MX5 HEV (내수 하이브리드)`, `MX5a (북미 수출형)`
3. **`Region` (판매 지역)**: `KR (대한민국)`, `US (미국)`, `SEA (동남아)`
4. **`SpecItem` (사양/옵션)**:
   - `1.6T 터보 하이브리드`, `2.5T 가솔린 터보`, `전자식 AWD`, `HUD (헤드업 디스플레이)`, `드라이브 와이즈 (HDA2)`, `빌트인 캠 2 (QHD)`, `파노라마 선루프`, `스마트 파워 테일게이트`
5. **`MarketingInfo` (마케팅/KSP 소구점)**:
   - `2025 신형 출시 일정 & 사전계약 혜택`, `동급 최고 패밀리 SUV 공간성 & 3열 독립시트`, `하이브리드 친환경차 세제혜택 & 복합연비 15.7km/L`, `북미 IIHS 톱 세이프티 픽 플러스(TSP+) 획득`, `시그니처 스타맵 라이팅`, `싼타페 H-라이트 & 테라스 테일게이트`

### B. 엣지 관계 (4대 Relationship Types)
1. `BELONGS_TO`: `ModelCode` ➔ `FamilyCar`
2. `AVAILABLE_IN`: `ModelCode` ➔ `Region`
3. `APPLIES_SPEC`: `ModelCode` ➔ `SpecItem`
4. `HAS_KSP`: `FamilyCar` 또는 `ModelCode` ➔ `MarketingInfo`

### C. 온톨로지 제약(Constraints) 및 공리(Axioms)
1. **`[Constraint]` 귀속성**: `ModelCode`는 반드시 1개의 `FamilyCar`에만 귀속(`BELONGS_TO`).
2. **`[Axiom]` 시장 적합성**: `Region='KR'`인 내수 `ModelCode`만 국내 사양 `SpecItem`과 `APPLIES_SPEC` 관계를 유효하게 연결.
3. **`[Weight Rule]` 비용 기반 동적 가중치 (Cost-based Dynamic Weights)**:
   - 가중치 값이 **0에 가까울수록** 현재 발화 의도와의 연관도(우선순위)가 높음.
   - **`INFO_SEARCH` (정보 탐색 의도)**: `HAS_KSP` = **0.1 (최우선 활성)**, `BELONGS_TO` = **0.2**, `AVAILABLE_IN` = **0.3**, `APPLIES_SPEC` = **0.9 (탐색 제외/후순위)**.
   - **`PURCHASE_INTENT` (실구매 의도)**: `APPLIES_SPEC` = **0.1 (최우선 활성)**, `BELONGS_TO` = **0.2**, `AVAILABLE_IN` = **0.3**, `HAS_KSP` = **0.9 (탐색 제외/후순위)**.

---

## 2. 10대 개발자 인기 IDE 테마 팔레트 (Light 4종 + Dark 6종)

사이드바 최상단에 `st.selectbox("🎨 IDE UI 테마 선택", [...])`를 제공하고, 선택된 테마에 맞춰 전체 UI 배경, 사이드바, 카드, 텍스트, 그래프 캔버스 및 노드 배색이 실시간 동기화되어야 합니다.

```python
THEMES = {
    # --- [Light Themes (4종)] ---
    "☀️ VS Code Light+": {
        "is_dark": False, "bg": "#FFFFFF", "sidebar_bg": "#F3F3F3", "card_bg": "#F8F9FA",
        "text": "#1E1E1E", "accent": "#007ACC", "border": "#E5E5E5", "graph_bg": "#FAFAFA",
        "node_colors": {"FamilyCar": "#007ACC", "ModelCode": "#D16969", "Region": "#098658", "MarketingInfo": "#AF00DB", "SpecItem": "#001080"}
    },
    "☀️ GitHub Light": {
        "is_dark": False, "bg": "#FFFFFF", "sidebar_bg": "#F6F8FA", "card_bg": "#F6F8FA",
        "text": "#24292F", "accent": "#0969DA", "border": "#D0D7DE", "graph_bg": "#FFFFFF",
        "node_colors": {"FamilyCar": "#0969DA", "ModelCode": "#CF222E", "Region": "#1A7F37", "MarketingInfo": "#8250DF", "SpecItem": "#953800"}
    },
    "☀️ One Light (Atom)": {
        "is_dark": False, "bg": "#FAFAFA", "sidebar_bg": "#EAEAEB", "card_bg": "#F0F0F1",
        "text": "#383A42", "accent": "#4078F2", "border": "#E0E0E1", "graph_bg": "#FDFDFD",
        "node_colors": {"FamilyCar": "#4078F2", "ModelCode": "#E45649", "Region": "#50A14F", "MarketingInfo": "#A626A4", "SpecItem": "#C18401"}
    },
    "☀️ Solarized Light": {
        "is_dark": False, "bg": "#FDF6E3", "sidebar_bg": "#EEE8D5", "card_bg": "#EEE8D5",
        "text": "#657B83", "accent": "#268BD2", "border": "#D33682", "graph_bg": "#FAF4E1",
        "node_colors": {"FamilyCar": "#268BD2", "ModelCode": "#CB4B16", "Region": "#859900", "MarketingInfo": "#D33682", "SpecItem": "#B58900"}
    },
    # --- [Dark Themes (6종)] ---
    "🌙 VS Code Dark+": {
        "is_dark": True, "bg": "#1E1E1E", "sidebar_bg": "#252526", "card_bg": "#2D2D2D",
        "text": "#D4D4D4", "accent": "#0E639C", "border": "#3E3E42", "graph_bg": "#1E1E1E",
        "node_colors": {"FamilyCar": "#4EC9B0", "ModelCode": "#CE9178", "Region": "#6A9955", "MarketingInfo": "#C586C0", "SpecItem": "#9CDCFE"}
    },
    "🌙 Dracula": {
        "is_dark": True, "bg": "#282A36", "sidebar_bg": "#21222C", "card_bg": "#343746",
        "text": "#F8F8F2", "accent": "#BD93F9", "border": "#44475A", "graph_bg": "#282A36",
        "node_colors": {"FamilyCar": "#8BE9FD", "ModelCode": "#FFB86C", "Region": "#50FA7B", "MarketingInfo": "#FF79C6", "SpecItem": "#F1FA8C"}
    },
    "🌙 One Dark Pro": {
        "is_dark": True, "bg": "#282C34", "sidebar_bg": "#21252B", "card_bg": "#2C313C",
        "text": "#ABB2BF", "accent": "#61AFEF", "border": "#3E4451", "graph_bg": "#282C34",
        "node_colors": {"FamilyCar": "#61AFEF", "ModelCode": "#D19A66", "Region": "#98C379", "MarketingInfo": "#C678DD", "SpecItem": "#E5C07B"}
    },
    "🌙 Monokai Pro": {
        "is_dark": True, "bg": "#2D2A2E", "sidebar_bg": "#221F22", "card_bg": "#363337",
        "text": "#FCFCFA", "accent": "#FFD866", "border": "#49464B", "graph_bg": "#2D2A2E",
        "node_colors": {"FamilyCar": "#78DCE8", "ModelCode": "#FC9867", "Region": "#A9DC76", "MarketingInfo": "#FF6188", "SpecItem": "#AB9DF2"}
    },
    "🌙 Nord": {
        "is_dark": True, "bg": "#2E3440", "sidebar_bg": "#242933", "card_bg": "#3B4252",
        "text": "#ECEFF4", "accent": "#88C0D0", "border": "#4C566A", "graph_bg": "#2E3440",
        "node_colors": {"FamilyCar": "#88C0D0", "ModelCode": "#D08770", "Region": "#A3BE8C", "MarketingInfo": "#B48EAD", "SpecItem": "#EBCB8B"}
    },
    "🌙 GitHub Dark Dimmed": {
        "is_dark": True, "bg": "#22272E", "sidebar_bg": "#1C2128", "card_bg": "#2D333B",
        "text": "#ADBAC7", "accent": "#539BF5", "border": "#444C56", "graph_bg": "#22272E",
        "node_colors": {"FamilyCar": "#539BF5", "ModelCode": "#F47067", "Region": "#57AB5A", "MarketingInfo": "#BC8CFF", "SpecItem": "#DCBDFB"}
    }
}
```

### [CSS 주입 및 구문 강조 핵심 규칙]
1. 일반 텍스트는 테마의 `text` 색상으로 강제 적용하되, 코드 블록 내부 Prism.js 토큰은 제외합니다:
   `.stApp span:not(pre span):not(code span):not([class*="token"]) { color: {text} !important; }`
2. `div[data-testid="stCodeBlock"] .token.keyword`, `.token.string`, `.token.comment` 등에 테마별 고유 구문 강조 색상을 주입하여 선명한 하이라이팅을 보장합니다.

---

## 3. UI/UX 레이아웃 구조 (Full-Width Top-Down Vertical Layout)

### A. 좌측 사이드바 (발화 시뮬레이션 및 파라미터 제어)
1. **🎨 IDE UI 테마 선택기**: Light 4종 + Dark 6종 전환.
2. **🗣️ 발화 선택 및 입력**:
   - Preset 1: "신형 소렌토 곧 나온다며?" (Intent: INFO_SEARCH)
   - Preset 2: "소렌토 구매하려고 하는데 옵션 추천해줘" (Intent: PURCHASE_INTENT)
   - Preset 3: "싼타페 하이브리드 신차 소식 알려줘" (Intent: INFO_SEARCH)
   - Preset 4: "싼타페 풀옵션 사양 및 견적 확인" (Intent: PURCHASE_INTENT)
   - 직접 입력 텍스트 박스 (`st.text_input`)
3. **🎯 의도 추론 및 시작 노드**:
   - `추론된 의도`: `INFO_SEARCH` vs `PURCHASE_INTENT` 라디오 버튼
   - `탐색 시작 노드 (Seed Node)`: `FamilyCar` 또는 `ModelCode` 선택 셀렉트박스
4. **⚙️ 온톨로지 탐색 파라미터**:
   - `Max Hop` (탐색 깊이: 1~3, 기본값 2)
   - `Edge Weight Threshold` (임계값: 0.0~1.0, 기본값 0.50) + 가중치 비용 원리 안내 박스
   - `지역 필터 (Region Constraint)`: `KR`, `US`, `ALL`

### B. 메인 패널 (위/아래 수직 전폭 배치)

#### [헤더 및 상단 KPI 메트릭 & 가이드]
1. 메인 타이틀 및 현재 의도/테마 상태 표시.
2. 온톨로지 가중치 탐색 원리 안내 카드.
3. 4대 KPI 메트릭 카드: `Active Subgraph Nodes`, `Active Traverse Edges`, `Query Execution Time (12.4ms)`, `Context Density Score (%)`.
4. **`💡 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드` Expander**:
   - `HAS_KSP` (마케팅 & 세일즈 관점 / Why to Buy) vs `APPLIES_SPEC` (실구매 & 기술 스펙 관점 / What is Inside) 비교 테이블 및 의도별 컨텍스트 제어 원리 설명.

#### [상단 영역] 🕸️ Interactive Knowledge Graph Visualization (Full Width, 710px)
1. **그래프 렌더링 엔진 선택 드롭다운**:
   - `1. PyVis (Vis.js 물리 시뮬레이션)`: `forceAtlas2Based` 물리 엔진, 마우스 휠 줌/팬, 노드 자유 드래그, 다크/라이트 배경 스트로크 폰트, 유니코드 카드형 텍스트 툴팁(HTML 이스케이프 문제 방지).
   - `2. Cytoscape.js (엔지니어링/구조적 레이아웃)`: COSE compound 레이아웃, 베지어 곡선 엣지, 테마별 색상 연동, 마우스 호버 위치 추적 플로팅 툴팁(`div#cy-tooltip`).
2. 범례 배지 박스 (FamilyCar, ModelCode, SpecItem, MarketingInfo, Region).

#### [하단 영역] ⚡ Dynamic Cypher/GQL Query & Grounding Result (3-Tabs)
- **Tab 1: 📝 BigQuery GQL Query**
  - 의도별 BigQuery 표준 GQL 쿼리 (`GRAPH ... MATCH ... WHERE ... RETURN ... ORDER BY ...`) 대문자 포맷팅.
  - BigQuery GoogleSQL `GRAPH_TABLE` 멀티홉 탐색 쿼리.
  - openCypher 표준 쿼리 Expander.
  - `language="sql"` 구문 강조 적용.
- **Tab 2: 🤖 LLM Grounding Context & Output**
  - 온톨로지 서브그래프 기반 RAG 응답 시뮬레이션 (`st.info`).
  - LLM 주입 프롬프트 컨텍스트 JSON (`st.json`).
- **Tab 3: 📊 Filtered Subgraph Tables**
  - 활성화된 노드 목록 테이블 (Node ID, Name, Type, Hop Distance, Cost, Relevance).
  - 활성화된 엣지 목록 테이블 (Source, Target, Relation, Weight, Description).

---

## 4. 기술 스택 및 실행 요구사항

- **Python 라이브러리**: `streamlit`, `pyvis`, `networkx`, `pandas`, `plotly`
- **구현 형태**: 외부 DB 연결 없이 즉시 `streamlit run app.py`로 구동 가능한 **단일 Python 파일 (`app.py`)** 완성형 코드.
- **오류 방지**: 최신 Streamlit 버전 호환 (`components.html` 렌더링, `hide_index=True`, 고대비 CSS 주입).
