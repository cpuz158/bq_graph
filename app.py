"""
Google Cloud BigQuery Graph & 시맨틱 온톨로지 탐색기 (Multi-Domain Knowledge Graph)
- 4대 비즈니스 도메인: 🚗 자동차 (Automotive) / 🛍️ 이커머스 (E-Commerce) / 📱 모바일 요금제 (Telco) / 🔬 반도체 8대 공정 (Semiconductor)
- 10대 IDE 테마 실시간 전환 (Light 4종 + Dark 6종)
- 4대 시각화 렌더러 (PyVis, Cytoscape.js, 3D Force Graph, AntV G6)
- BigQuery GQL & GoogleSQL GRAPH_TABLE 구문 강조 및 LLM Context Grounding 시뮬레이터 (단일 파일: app.py)
"""

import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network
import pandas as pd
import json

# ==========================================
# 0. 10대 개발자 인기 IDE 테마 팔레트 정의
# ==========================================
THEMES = {
    # --- [Light Themes (4종)] ---
    "☀️ VS Code Light+": {
        "is_dark": False, "bg": "#FFFFFF", "sidebar_bg": "#F3F3F3", "card_bg": "#F8F9FA",
        "text": "#1E1E1E", "accent": "#007ACC", "border": "#E5E5E5", "graph_bg": "#FAFAFA",
        "node_colors": {"Parent": "#007ACC", "Child": "#D16969", "Filter": "#098658", "Marketing": "#AF00DB", "Spec": "#001080"}
    },
    "☀️ GitHub Light": {
        "is_dark": False, "bg": "#FFFFFF", "sidebar_bg": "#F6F8FA", "card_bg": "#F6F8FA",
        "text": "#24292F", "accent": "#0969DA", "border": "#D0D7DE", "graph_bg": "#FFFFFF",
        "node_colors": {"Parent": "#0969DA", "Child": "#CF222E", "Filter": "#1A7F37", "Marketing": "#8250DF", "Spec": "#953800"}
    },
    "☀️ One Light (Atom)": {
        "is_dark": False, "bg": "#FAFAFA", "sidebar_bg": "#EAEAEB", "card_bg": "#F0F0F1",
        "text": "#383A42", "accent": "#4078F2", "border": "#E0E0E1", "graph_bg": "#FDFDFD",
        "node_colors": {"Parent": "#4078F2", "Child": "#E45649", "Filter": "#50A14F", "Marketing": "#A626A4", "Spec": "#C18401"}
    },
    "☀️ Solarized Light": {
        "is_dark": False, "bg": "#FDF6E3", "sidebar_bg": "#EEE8D5", "card_bg": "#EEE8D5",
        "text": "#657B83", "accent": "#268BD2", "border": "#D33682", "graph_bg": "#FAF4E1",
        "node_colors": {"Parent": "#268BD2", "Child": "#CB4B16", "Filter": "#859900", "Marketing": "#D33682", "Spec": "#B58900"}
    },
    # --- [Dark Themes (6종)] ---
    "🌙 VS Code Dark+": {
        "is_dark": True, "bg": "#1E1E1E", "sidebar_bg": "#252526", "card_bg": "#2D2D2D",
        "text": "#D4D4D4", "accent": "#0E639C", "border": "#3E3E42", "graph_bg": "#1E1E1E",
        "node_colors": {"Parent": "#4EC9B0", "Child": "#CE9178", "Filter": "#6A9955", "Marketing": "#C586C0", "Spec": "#9CDCFE"}
    },
    "🌙 Dracula": {
        "is_dark": True, "bg": "#282A36", "sidebar_bg": "#21222C", "card_bg": "#343746",
        "text": "#F8F8F2", "accent": "#BD93F9", "border": "#44475A", "graph_bg": "#282A36",
        "node_colors": {"Parent": "#8BE9FD", "Child": "#FFB86C", "Filter": "#50FA7B", "Marketing": "#FF79C6", "Spec": "#F1FA8C"}
    },
    "🌙 One Dark Pro": {
        "is_dark": True, "bg": "#282C34", "sidebar_bg": "#21252B", "card_bg": "#2C313C",
        "text": "#ABB2BF", "accent": "#61AFEF", "border": "#3E4451", "graph_bg": "#282C34",
        "node_colors": {"Parent": "#61AFEF", "Child": "#D19A66", "Filter": "#98C379", "Marketing": "#C678DD", "Spec": "#E5C07B"}
    },
    "🌙 Monokai Pro": {
        "is_dark": True, "bg": "#2D2A2E", "sidebar_bg": "#221F22", "card_bg": "#363337",
        "text": "#FCFCFA", "accent": "#FFD866", "border": "#49464B", "graph_bg": "#2D2A2E",
        "node_colors": {"Parent": "#78DCE8", "Child": "#FC9867", "Filter": "#A9DC76", "Marketing": "#FF6188", "Spec": "#AB9DF2"}
    },
    "🌙 Nord": {
        "is_dark": True, "bg": "#2E3440", "sidebar_bg": "#242933", "card_bg": "#3B4252",
        "text": "#ECEFF4", "accent": "#88C0D0", "border": "#4C566A", "graph_bg": "#2E3440",
        "node_colors": {"Parent": "#88C0D0", "Child": "#D08770", "Filter": "#A3BE8C", "Marketing": "#B48EAD", "Spec": "#EBCB8B"}
    },
    "🌙 GitHub Dark Dimmed": {
        "is_dark": True, "bg": "#22272E", "sidebar_bg": "#1C2128", "card_bg": "#2D333B",
        "text": "#ADBAC7", "accent": "#539BF5", "border": "#444C56", "graph_bg": "#22272E",
        "node_colors": {"Parent": "#539BF5", "Child": "#F47067", "Filter": "#57AB5A", "Marketing": "#BC8CFF", "Spec": "#DCBDFB"}
    }
}


def get_theme_node_color_map(theme: dict, domain_meta: dict) -> dict:
    """
    도메인의 5대 노드 타입을 현재 테마의 팔레트에 매핑합니다.
    """
    palette = theme["node_colors"]
    return {
        domain_meta["parent_type"]: palette["Parent"],
        domain_meta["child_type"]: palette["Child"],
        domain_meta["filter_type"]: palette["Filter"],
        domain_meta["mkt_type"]: palette["Marketing"],
        domain_meta["spec_type"]: palette["Spec"]
    }


def generate_theme_css(theme: dict, domain_meta: dict) -> str:
    """
    선택된 IDE 테마 팔레트에 따라 Streamlit 전체 UI 스타일 및 Prism.js 구문 강조 CSS를 동적 주입합니다.
    """
    is_dark = theme.get("is_dark", True)
    bg = theme["bg"]
    sidebar_bg = theme["sidebar_bg"]
    card_bg = theme["card_bg"]
    text = theme["text"]
    accent = theme["accent"]
    border = theme["border"]
    node_colors = get_theme_node_color_map(theme, domain_meta)

    p_col = node_colors.get(domain_meta["parent_type"], "#007ACC")
    c_col = node_colors.get(domain_meta["child_type"], "#D16969")
    f_col = node_colors.get(domain_meta["filter_type"], "#098658")
    m_col = node_colors.get(domain_meta["mkt_type"], "#AF00DB")
    s_col = node_colors.get(domain_meta["spec_type"], "#001080")

    if is_dark:
        code_bg = sidebar_bg
        token_keyword = "#C678DD"
        token_string = "#98C379"
        token_comment = "#7F848E"
        token_number = "#D19A66"
        token_function = "#61AFEF"
        token_operator = "#56B6C2"
        token_punct = "#ABB2BF"
    else:
        code_bg = "#F6F8FA" if bg == "#FFFFFF" else "#EAEAEB"
        token_keyword = "#005CC5"
        token_string = "#22863A"
        token_comment = "#6A737D"
        token_number = "#E36209"
        token_function = "#6F42C1"
        token_operator = "#D73A49"
        token_punct = "#24292F"

    return f"""
<style>
    /* 1. 전체 앱 및 사이드바 배경/글자색 강제 */
    .stApp, [data-testid="stAppViewContainer"], .main, header[data-testid="stHeader"] {{
        background-color: {bg} !important;
        color: {text} !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border} !important;
    }}

    /* 2. 일반 텍스트 및 제목 (코드 블록 내부 토큰 span은 명시적으로 제외) */
    .stApp p:not(pre p):not(code p),
    .stApp span:not(pre span):not(code span):not([class*="token"]),
    .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp li, .stApp b, .stApp strong, .stApp small, .stMarkdown, .stCaption {{
        color: {text} !important;
    }}

    /* 3. 사이드바 내부 텍스트, 라벨, 컨트롤 */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span:not([class*="token"]),
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] .stMarkdown {{
        color: {text} !important;
    }}

    /* 4. 입력 위젯 */
    [data-baseweb="radio"] span, [data-baseweb="radio"] label {{
        color: {text} !important;
    }}
    [data-baseweb="select"] div, [data-baseweb="select"] span {{
        color: {text} !important;
        background-color: {card_bg} !important;
    }}
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
    }}
    ul[role="listbox"] li, ul[role="listbox"] li span {{
        color: {text} !important;
        background-color: {card_bg} !important;
    }}
    input[type="text"], input[type="number"], .stTextInput input {{
        background-color: {card_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
    }}

    /* 5. KPI 메트릭 카드 */
    .metric-card {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 10px;
        padding: 14px 18px;
        color: {text} !important;
        box-shadow: 0 4px 6px -1px {'rgba(0, 0, 0, 0.3)' if is_dark else 'rgba(0, 0, 0, 0.06)'};
    }}
    .metric-title {{
        font-size: 0.82rem;
        color: {text} !important;
        opacity: 0.85;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-value {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {accent} !important;
        margin-top: 4px;
    }}

    /* 6. 가이드 카드 컴포넌트 */
    .main-guide-card {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 10px;
        padding: 14px 18px;
        color: {text} !important;
        margin-bottom: 16px;
        font-size: 0.88rem;
    }}
    .weight-guide-box {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        border-left: 4px solid {accent} !important;
        border-radius: 6px;
        padding: 12px 14px;
        font-size: 0.82rem;
        color: {text} !important;
        line-height: 1.5;
        margin-top: 10px;
        margin-bottom: 12px;
    }}

    /* 7. 범례 박스 및 테마별 노드 배지 */
    .legend-box {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px;
        margin-bottom: 12px;
    }}
    .badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
    }}
    .badge-node-parent {{ background-color: {p_col}{'30' if is_dark else '18'} !important; color: {p_col} !important; border: 1px solid {p_col} !important; }}
    .badge-node-child {{ background-color: {c_col}{'30' if is_dark else '18'} !important; color: {c_col} !important; border: 1px solid {c_col} !important; }}
    .badge-node-filter {{ background-color: {f_col}{'30' if is_dark else '18'} !important; color: {f_col} !important; border: 1px solid {f_col} !important; }}
    .badge-node-marketing {{ background-color: {m_col}{'30' if is_dark else '18'} !important; color: {m_col} !important; border: 1px solid {m_col} !important; }}
    .badge-node-spec {{ background-color: {s_col}{'30' if is_dark else '18'} !important; color: {s_col} !important; border: 1px solid {s_col} !important; }}

    /* 8. Expander, 탭, 테이블 */
    .streamlit-expanderHeader, [data-testid="stExpander"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary {{
        background-color: {card_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}
    [data-testid="stExpander"] summary span, [data-testid="stExpander"] summary p {{
        color: {text} !important;
    }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
        background-color: {card_bg} !important;
        color: {text} !important;
    }}
    [data-testid="stExpander"] table, [data-testid="stExpander"] th, [data-testid="stExpander"] td {{
        color: {text} !important;
        border-color: {border} !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 1px solid {border} !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {text} !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {accent} !important;
        border-bottom-color: {accent} !important;
    }}
    div[data-testid="stDataFrame"], [data-testid="stTable"] {{
        background-color: {card_bg} !important;
        color: {text} !important;
    }}
    div[data-testid="stDataFrame"] * {{
        color: {text} !important;
    }}
    [data-testid="stAlert"] {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
    }}
    [data-testid="stAlert"] * {{
        color: {text} !important;
    }}

    /* 9. Prism.js 코드 블록 구문 강조 복원 */
    div[data-testid="stCodeBlock"], .stCodeBlock {{
        background-color: {code_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stCodeBlock"] pre,
    div[data-testid="stCodeBlock"] code {{
        background-color: transparent !important;
        font-family: 'Fira Code', 'Cascadia Code', 'Consolas', 'Monaco', monospace !important;
        font-size: 13.5px !important;
        line-height: 1.6 !important;
    }}
    div[data-testid="stCodeBlock"] .token.keyword {{ color: {token_keyword} !important; font-weight: 700 !important; }}
    div[data-testid="stCodeBlock"] .token.string {{ color: {token_string} !important; }}
    div[data-testid="stCodeBlock"] .token.comment {{ color: {token_comment} !important; font-style: italic !important; }}
    div[data-testid="stCodeBlock"] .token.number {{ color: {token_number} !important; font-weight: 600 !important; }}
    div[data-testid="stCodeBlock"] .token.function {{ color: {token_function} !important; }}
    div[data-testid="stCodeBlock"] .token.operator {{ color: {token_operator} !important; }}
    div[data-testid="stCodeBlock"] .token.punctuation {{ color: {token_punct} !important; }}
    div[data-testid="stCodeBlock"] .token.class-name {{ color: {accent} !important; }}
    div[data-testid="stCodeBlock"] .token.property {{ color: {token_keyword} !important; }}
</style>
"""


# =========================================================================
# 1. 3대 비즈니스 도메인 온톨로지 데이터 생성기 (Automotive / E-Commerce / Telco)
# =========================================================================
def generate_domain_data(domain: str):
    """
    선택된 비즈니스 도메인에 따라 노드, 엣지 및 도메인 메타데이터를 반환합니다.
    (모든 노드 라벨에 가격/비용/할인 태그가 상시 노출되도록 포함)
    """
    if domain.startswith("🚗"):
        # -------------------------------------------------------------
        # 도메인 1: 🚗 자동차 (Automotive)
        # -------------------------------------------------------------
        domain_meta = {
            "id": "automotive",
            "name": "🚗 자동차 (Automotive)",
            "bq_dataset": "gcp-project-auto-kg.vehicle_ontology.auto_semantic_graph",
            "parent_type": "FamilyCar",
            "parent_label": "FamilyCar (차종)",
            "child_type": "ModelCode",
            "child_label": "ModelCode (모델코드/가격)",
            "filter_type": "Region",
            "filter_label": "판매지역 (Region)",
            "mkt_type": "MarketingInfo",
            "mkt_label": "MarketingInfo (프로모션/할인)",
            "spec_type": "SpecItem",
            "spec_label": "SpecItem (옵션/추가가격)",
            "rel_belongs": "BELONGS_TO",
            "rel_filter": "AVAILABLE_IN",
            "rel_mkt": "HAS_KSP",
            "rel_spec": "APPLIES_SPEC",
            "filter_param_name": "지역 필터 (Region Constraint)",
            "filter_options": ["KR", "US", "ALL"],
            "filter_options_labels": {"KR": "KR (대한민국 내수)", "US": "US (미국 시장)", "ALL": "ALL (전체 지역)"},
            "presets": [
                {"label": "Preset 1: '신형 소렌토 곧 나온다며?' (마케팅/할인 혜택)", "query": "신형 소렌토 곧 나온다며?", "intent": "INFO_SEARCH", "seed": "FC_SORENTO", "max_hop": 2, "weight_threshold": 0.50, "filter": "KR"},
                {"label": "Preset 2: '소렌토 구매하려고 하는데 옵션 추천해줘' (실구매/출고가/옵션가)", "query": "소렌토 구매하려고 하는데 옵션 추천해줘", "intent": "PURCHASE_INTENT", "seed": "FC_SORENTO", "max_hop": 2, "weight_threshold": 0.50, "filter": "KR"},
                {"label": "Preset 3: '싼타페 하이브리드 신차 소식 알려줘' (마케팅/할인 혜택)", "query": "싼타페 하이브리드 신차 소식 알려줘", "intent": "INFO_SEARCH", "seed": "FC_SANTAFE", "max_hop": 2, "weight_threshold": 0.50, "filter": "KR"},
                {"label": "Preset 4: '싼타페 풀옵션 사양 및 견적 확인' (실구매/출고가/옵션가)", "query": "싼타페 풀옵션 사양 및 견적 확인", "intent": "PURCHASE_INTENT", "seed": "FC_SANTAFE", "max_hop": 2, "weight_threshold": 0.50, "filter": "KR"}
            ]
        }

        nodes = [
            {"id": "FC_SORENTO", "name": "소렌토 (Sorento)", "type": "FamilyCar", "desc": "기아 대표 중형 패밀리 SUV", "attributes": {"segment": "Midsize SUV", "manufacturer": "Kia", "seats": "5/6/7인승"}},
            {"id": "FC_SANTAFE", "name": "싼타페 (Santa Fe)", "type": "FamilyCar", "desc": "현대 대표 도심형/아웃도어 패밀리 SUV", "attributes": {"segment": "Midsize SUV", "manufacturer": "Hyundai", "seats": "5/6/7인승"}},
            {"id": "MC_MQ4_KR", "name": "MQ4 내수 가솔린/디젤 [3,500만원~]", "type": "ModelCode", "desc": "4세대 소렌토 국내 내연기관 모델 (기본 출고가)", "attributes": {"generation": "4th Gen", "powertrain": "2.5T / 2.2D", "base_price": "3,500만원~", "base_price_num": 35000000, "market": "KR"}},
            {"id": "MC_MQ4_HEV_KR", "name": "MQ4 HEV 하이브리드 [3,780만원~]", "type": "ModelCode", "desc": "4세대 소렌토 국내 터보 하이브리드 인기 모델", "attributes": {"generation": "4th Gen", "powertrain": "1.6T HEV", "base_price": "3,780만원~", "base_price_num": 37800000, "market": "KR"}},
            {"id": "MC_MQ4_US", "name": "MQ4a 북미 수출형 [$31,990~]", "type": "ModelCode", "desc": "소렌토 북미 조지아 공장 생산형 (MSRP 기준)", "attributes": {"generation": "4th Gen", "powertrain": "2.5T / 1.6T HEV", "base_price": "$31,990~", "base_price_num": 31990, "market": "US"}},
            {"id": "MC_MX5_KR", "name": "MX5 가솔린 2.5T [3,540만원~]", "type": "ModelCode", "desc": "5세대 디 올 뉴 싼타페 국내 가솔린 모델", "attributes": {"generation": "5th Gen", "powertrain": "2.5T", "base_price": "3,540만원~", "base_price_num": 35400000, "market": "KR"}},
            {"id": "MC_MX5_HEV_KR", "name": "MX5 HEV 하이브리드 [3,880만원~]", "type": "ModelCode", "desc": "5세대 디 올 뉴 싼타페 국내 터보 하이브리드 모델", "attributes": {"generation": "5th Gen", "powertrain": "1.6T HEV", "base_price": "3,880만원~", "base_price_num": 38800000, "market": "KR"}},
            {"id": "MC_MX5_US", "name": "MX5a 북미 수출형 [$33,950~]", "type": "ModelCode", "desc": "싼타페 북미 수출 및 현지 생산형 (MSRP 기준)", "attributes": {"generation": "5th Gen", "powertrain": "2.5T AWD", "base_price": "$33,950~", "base_price_num": 33950, "market": "US"}},
            {"id": "REG_KR", "name": "KR (대한민국)", "type": "Region", "desc": "국내 내수 시장 (K-Certification / 국내 보증)", "attributes": {"code": "KR", "currency": "KRW", "ev_subsidy": "적용"}},
            {"id": "REG_US", "name": "US (미국)", "type": "Region", "desc": "북미 시장 (EPA / IIHS 규격)", "attributes": {"code": "US", "currency": "USD", "safety_std": "FMVSS"}},
            {"id": "REG_SEA", "name": "SEA (동남아)", "type": "Region", "desc": "동남아 아세안 시장 (우핸들/열대 특화)", "attributes": {"code": "SEA", "currency": "USD/Local", "climate": "Tropical"}},
            {"id": "SPEC_HEV_16T", "name": "1.6T HEV 전용 엔진 (+기본포함)", "type": "SpecItem", "desc": "최고출력 245ps(합산), 복합연비 15.7km/L 터보 하이브리드 엔진", "attributes": {"category": "Powertrain", "option_price": "0원 (기본포함)", "efficiency": "15.7 km/L", "power": "245 ps"}},
            {"id": "SPEC_GAS_25T", "name": "2.5T 가솔린 AWD (+$2,000)", "type": "SpecItem", "desc": "최고출력 281ps, 최대토크 43.0kgf·m 스마트스트림 G2.5T 북미 사양", "attributes": {"category": "Powertrain", "option_price": "$2,000", "power": "281 ps", "torque": "43.0 kgf·m"}},
            {"id": "SPEC_AWD", "name": "전자식 AWD 4륜구동 (+200만원)", "type": "SpecItem", "desc": "지형 반응 모드(터레인 모드: Snow/Mud/Sand) 연동 전자식 4WD", "attributes": {"category": "Drivetrain", "option_price": "200만원", "terrain_mode": "Auto/Snow/Mud/Sand"}},
            {"id": "SPEC_HUD", "name": "10인치 헤드업 디스플레이 (+70만원)", "type": "SpecItem", "desc": "10인치 윈드실드 타입 고해상도 그래픽 HUD", "attributes": {"category": "Convenience", "option_price": "70만원", "size": "10 inch"}},
            {"id": "SPEC_DRIVEWISE", "name": "드라이브 와이즈 ADAS (+120만원)", "type": "SpecItem", "desc": "HDA2, 전방 충돌방지 보조, 스마트 크루즈(정차&재출발) 안전 패키지", "attributes": {"category": "Safety / ADAS", "option_price": "120만원", "level": "Level 2+"}},
            {"id": "SPEC_BUILTINCAM2", "name": "QHD 빌트인 캠 2 (+45만원)", "type": "SpecItem", "desc": "전후방 QHD 고화질 녹화, 음성녹음 및 증강현실 내비게이션 지원", "attributes": {"category": "Electronics", "option_price": "45만원", "resolution": "QHD"}},
            {"id": "SPEC_PANORAMA_SUNROOF", "name": "와이드 파노라마 선루프 (+110만원)", "type": "SpecItem", "desc": "와이드 오픈 파노라마 선루프 & 전동 롤 블라인드", "attributes": {"category": "Exterior", "option_price": "110만원", "type": "Wide Electric"}},
            {"id": "MKT_2025_RELEASE", "name": "2025 페이스리프트 (사전예약 혜택 50만원)", "type": "MarketingInfo", "desc": "2025년형 페이스리프트 출시 일정 확정, 연 2.9% 저금리 & 50만원 바우처 지원", "attributes": {"target_date": "2025 Q3", "discount": "50만원 바우처", "benefit": "연 2.9% 저금리"}},
            {"id": "MKT_FAMILY_SPACE", "name": "패밀리 공간성 (2열 독립시트 무상)", "type": "MarketingInfo", "desc": "2,815mm 동급 최장 휠베이스, 2열 독립 캡틴시트 무상 업그레이드 프로모션", "attributes": {"wheelbase": "2,815 mm", "discount": "무상 업그레이드"}},
            {"id": "MKT_HEV_BENEFIT", "name": "친환경차 세제혜택 (최대 143만원 감면)", "type": "MarketingInfo", "desc": "개별소비세/취득세 최대 143만원 감면 및 공영주차장 50% 할인 혜택", "attributes": {"discount": "최대 143만원 감면", "benefit": "공영주차장 50%"}},
            {"id": "MKT_SAFETY_TSP", "name": "북미 IIHS TSP+ 최고안전등급 (보험료 10% 감면)", "type": "MarketingInfo", "desc": "미국 IIHS 충돌 평가 최고 등급 획득 및 10-에어백 기본 탑재", "attributes": {"rating": "IIHS TSP+", "discount": "보험료 10% 감면"}},
            {"id": "MKT_DESIGN_STARMAP", "name": "스타맵 라이팅 (스타일 패키지 30만 할인)", "type": "MarketingInfo", "desc": "기아 최신 수직형 헤드램프 및 12.3인치 듀얼 파노라믹 디스플레이", "attributes": {"discount": "30만원 할인", "cluster": "12.3인치 파노라믹"}},
            {"id": "MKT_SANTAFE_HLIGHT", "name": "테라스 테일게이트 (아웃도어 패키지 40만 지원)", "type": "MarketingInfo", "desc": "현대 엠블럼 재해석 H-시그니처 램프와 아웃도어 특화 대형 테일게이트", "attributes": {"discount": "40만원 지원", "concept": "Open for More"}}
        ]

        edges = [
            {"source": "MC_MQ4_KR", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 모델 라인업 귀속"},
            {"source": "MC_MQ4_HEV_KR", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 하이브리드 라인업 귀속"},
            {"source": "MC_MQ4_US", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 북미 모델 라인업 귀속"},
            {"source": "MC_MX5_KR", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 모델 라인업 귀속"},
            {"source": "MC_MX5_HEV_KR", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 하이브리드 라인업 귀속"},
            {"source": "MC_MX5_US", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 북미 모델 라인업 귀속"},
            {"source": "MC_MQ4_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
            {"source": "MC_MQ4_HEV_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
            {"source": "MC_MQ4_US", "target": "REG_US", "relation": "AVAILABLE_IN", "desc": "미국 시장 판매"},
            {"source": "MC_MX5_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
            {"source": "MC_MX5_HEV_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
            {"source": "MC_MX5_US", "target": "REG_US", "relation": "AVAILABLE_IN", "desc": "미국 시장 판매"},
            {"source": "MC_MQ4_KR", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "2.5T 가솔린 터보 탑재"},
            {"source": "MC_MQ4_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "선택 사양 전자식 4WD"},
            {"source": "MC_MQ4_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "선택 사양 HUD"},
            {"source": "MC_MQ4_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "선택 사양 드라이브 와이즈"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_HEV_16T", "relation": "APPLIES_SPEC", "desc": "1.6T 터보 하이브리드 탑재"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "e-AWD 4륜구동"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "선택 사양 HUD"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "드라이브 와이즈 패키지"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_BUILTINCAM2", "relation": "APPLIES_SPEC", "desc": "선택 사양 QHD 빌트인 캠 2"},
            {"source": "MC_MQ4_HEV_KR", "target": "SPEC_PANORAMA_SUNROOF", "relation": "APPLIES_SPEC", "desc": "선택 사양 파노라마 선루프"},
            {"source": "MC_MQ4_US", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "북미 2.5T 가솔린 사양"},
            {"source": "MC_MQ4_US", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "북미 X-Line AWD"},
            {"source": "MC_MX5_KR", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "2.5T 가솔린 사양"},
            {"source": "MC_MX5_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "HTRAC 전자식 AWD"},
            {"source": "MC_MX5_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "헤드업 디스플레이"},
            {"source": "MC_MX5_HEV_KR", "target": "SPEC_HEV_16T", "relation": "APPLIES_SPEC", "desc": "1.6T 터보 하이브리드 사양"},
            {"source": "MC_MX5_HEV_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "HTRAC 하이브리드 AWD"},
            {"source": "MC_MX5_HEV_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "스마트센스 (HDA2 포함)"},
            {"source": "MC_MX5_HEV_KR", "target": "SPEC_BUILTINCAM2", "relation": "APPLIES_SPEC", "desc": "빌트인 캠 2"},
            {"source": "MC_MX5_US", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "북미 2.5T 가솔린 사양"},
            {"source": "FC_SORENTO", "target": "MKT_2025_RELEASE", "relation": "HAS_KSP", "desc": "소렌토 신형 출시 일정 & 사전계약"},
            {"source": "FC_SORENTO", "target": "MKT_FAMILY_SPACE", "relation": "HAS_KSP", "desc": "소렌토 동급 최대 실내공간"},
            {"source": "FC_SORENTO", "target": "MKT_DESIGN_STARMAP", "relation": "HAS_KSP", "desc": "소렌토 스타맵 라이팅 KSP"},
            {"source": "MC_MQ4_HEV_KR", "target": "MKT_HEV_BENEFIT", "relation": "HAS_KSP", "desc": "소렌토 하이브리드 세제혜택 & 연비"},
            {"source": "MC_MQ4_US", "target": "MKT_SAFETY_TSP", "relation": "HAS_KSP", "desc": "소렌토 북미 IIHS 안전등급"},
            {"source": "FC_SANTAFE", "target": "MKT_SANTAFE_HLIGHT", "relation": "HAS_KSP", "desc": "싼타페 H-라이트 & 테라스 테일게이트"},
            {"source": "FC_SANTAFE", "target": "MKT_FAMILY_SPACE", "relation": "HAS_KSP", "desc": "싼타페 3열 대형 실내공간"},
            {"source": "MC_MX5_HEV_KR", "target": "MKT_HEV_BENEFIT", "relation": "HAS_KSP", "desc": "싼타페 하이브리드 친환경 혜택"},
            {"source": "MC_MX5_US", "target": "MKT_SAFETY_TSP", "relation": "HAS_KSP", "desc": "싼타페 북미 IIHS 안전등급"}
        ]

    elif domain.startswith("🛍️"):
        # -------------------------------------------------------------
        # 도메인 2: 🛍️ 이커머스 (E-Commerce)
        # -------------------------------------------------------------
        domain_meta = {
            "id": "ecommerce",
            "name": "🛍️ 이커머스 (E-Commerce)",
            "bq_dataset": "gcp-project-ecommerce.catalog_ontology.product_semantic_graph",
            "parent_type": "BrandCategory",
            "parent_label": "BrandCategory (브랜드/카테고리)",
            "child_type": "ProductSKU",
            "child_label": "ProductSKU (상품 SKU/정가)",
            "filter_type": "TargetSegment",
            "filter_label": "타깃 세그먼트 (Target Segment)",
            "mkt_type": "PromoEvent",
            "mkt_label": "PromoEvent (기획전/쿠폰할인)",
            "spec_type": "ProductSpec",
            "spec_label": "ProductSpec (상세 스펙/사양가치)",
            "rel_belongs": "BELONGS_TO",
            "rel_filter": "TARGETS",
            "rel_mkt": "HAS_PROMO",
            "rel_spec": "APPLIES_SPEC",
            "filter_param_name": "고객 세그먼트 필터 (Target Segment)",
            "filter_options": ["SEG_BEGINNER", "SEG_MARATHON", "ALL"],
            "filter_options_labels": {"SEG_BEGINNER": "입문/초보 러너 (Beginner)", "SEG_MARATHON": "마라톤 풀코스/엘리트 (Marathon)", "ALL": "ALL (전체 세그먼트)"},
            "presets": [
                {"label": "Preset 1: '요즘 인기 있는 러닝화 기획전 있어?' (프로모션/쿠폰할인)", "query": "요즘 인기 있는 러닝화 기획전 있어?", "intent": "INFO_SEARCH", "seed": "BC_NIKE_RUNNING", "max_hop": 2, "weight_threshold": 0.50, "filter": "SEG_BEGINNER"},
                {"label": "Preset 2: '페가수스 41 쿠셔닝 폼이랑 무게 스펙 알려줘' (상품 판매가/스펙가치)", "query": "페가수스 41 쿠셔닝 폼이랑 무게 스펙 알려줘", "intent": "PURCHASE_INTENT", "seed": "BC_NIKE_RUNNING", "max_hop": 2, "weight_threshold": 0.50, "filter": "SEG_BEGINNER"},
                {"label": "Preset 3: '봄맞이 캠핑 텐트 할인 프로모션 확인' (프로모션/기프트)", "query": "봄맞이 캠핑 텐트 할인 프로모션 확인", "intent": "INFO_SEARCH", "seed": "BC_CAMPING_TENT", "max_hop": 2, "weight_threshold": 0.50, "filter": "SEG_BEGINNER"},
                {"label": "Preset 4: '알파플라이 3 카본 플레이트 및 마라톤 사양 비교' (프리미엄가/사양)", "query": "알파플라이 3 카본 플레이트 및 마라톤 사양 비교", "intent": "PURCHASE_INTENT", "seed": "BC_NIKE_RUNNING", "max_hop": 2, "weight_threshold": 0.50, "filter": "SEG_MARATHON"}
            ]
        }

        nodes = [
            {"id": "BC_NIKE_RUNNING", "name": "나이키 러닝 (Nike Running)", "type": "BrandCategory", "desc": "글로벌 No.1 퍼포먼스 러닝화 라인업", "attributes": {"category": "Footwear", "brand": "Nike", "season": "2025 S/S"}},
            {"id": "BC_CAMPING_TENT", "name": "프리미엄 캠핑 텐트 (Camping Tent)", "type": "BrandCategory", "desc": "사계절 패밀리 오토캠핑 및 쉘터 라인업", "attributes": {"category": "Outdoor", "brand": "SnowPeak / Helinox", "season": "2025 S/S"}},
            {"id": "SKU_PEGASUS_41", "name": "나이키 페가수스 41 [159,000원]", "type": "ProductSKU", "desc": "국민 데일리 트레이닝 러닝화 (정가 15.9만원)", "attributes": {"price": "159,000원", "price_num": 159000, "weight": "281g", "market": "SEG_BEGINNER"}},
            {"id": "SKU_ALPHAFLY_3", "name": "에어줌 알파플라이 3 [359,000원]", "type": "ProductSKU", "desc": "세계 마라톤 신기록 수립 엘리트 레이싱화 (정가 35.9만원)", "attributes": {"price": "359,000원", "price_num": 359000, "weight": "218g", "market": "SEG_MARATHON"}},
            {"id": "SKU_VAPORFLY_3", "name": "줌엑스 베이퍼플라이 3 [299,000원]", "type": "ProductSKU", "desc": "하프/풀코스 로드 레이싱 올라운더 레이서 (정가 29.9만원)", "attributes": {"price": "299,000원", "price_num": 299000, "weight": "198g", "market": "SEG_MARATHON"}},
            {"id": "SKU_DOME_TENT_4P", "name": "어메니티 돔 4인용 [498,000원]", "type": "ProductSKU", "desc": "초보자도 10분 설치 가능한 패밀리 돔 텐트 (정가 49.8만원)", "attributes": {"price": "498,000원", "price_num": 498000, "capacity": "4인", "market": "SEG_BEGINNER"}},
            {"id": "SKU_TUNNEL_SHELTER", "name": "랜드락 대형 투룸 쉘터 [1,980,000원]", "type": "ProductSKU", "desc": "광활한 거실형 사계절 대형 패밀리 쉘터 (정가 198만원)", "attributes": {"price": "1,980,000원", "price_num": 1980000, "capacity": "6인", "market": "SEG_MARATHON"}},
            {"id": "SEG_BEGINNER", "name": "입문/초보 러너 & 캠퍼", "type": "TargetSegment", "desc": "가성비와 편안함, 쉬운 사용성을 중시하는 입문 고객군", "attributes": {"code": "SEG_BEGINNER", "experience": "Entry / Intermediate"}},
            {"id": "SEG_MARATHON", "name": "마라톤 풀코스 & 헤비 캠퍼", "type": "TargetSegment", "desc": "서브-3 기록 단축 및 익스트림 아웃도어 매니아", "attributes": {"code": "SEG_MARATHON", "experience": "Advanced / Pro"}},
            {"id": "SPEC_ZOOMX_FOAM", "name": "ZoomX 고반발 폼 (+핵심 사양)", "type": "ProductSpec", "desc": "에너지 리턴 85%의 항공우주 등급 초경량 미드솔 폼", "attributes": {"category": "Midsole", "spec_value": "기본탑재 (반발력 85%)", "option_price": "핵심 기본탑재"}},
            {"id": "SPEC_CARBON_PLATE", "name": "풀렝스 카본 플라이플레이트 (+프리미엄)", "type": "ProductSpec", "desc": "추진력을 극대화하는 전족부-후족부 일체형 탄소섬유판", "attributes": {"category": "Plate", "spec_value": "선수용옵션 (카본 100%)", "option_price": "프리미엄 옵션"}},
            {"id": "SPEC_REACTX_FOAM", "name": "ReactX 쿠셔닝 폼 (+친환경 에코)", "type": "ProductSpec", "desc": "탄소 배출량 43% 감축 및 13% 향상된 쿠셔닝 제공", "attributes": {"category": "Midsole", "spec_value": "기본탑재", "option_price": "친환경 기본사양"}},
            {"id": "SPEC_WATERPROOF_3000", "name": "내수압 3,000mm 립스탑 (+고내수압 원단)", "type": "ProductSpec", "desc": "폭우와 강풍을 완벽 차단하는 고밀도 75D 테프론 발수 코팅", "attributes": {"category": "Fabric", "spec_value": "테프론 발수 가공", "option_price": "고급 원단사양"}},
            {"id": "SPEC_ALU_POLE", "name": "두랄루민 7001 폴대 (+초경량 고강도)", "type": "ProductSpec", "desc": "항공기용 고강도 경량 알루미늄 폴대 프레임", "attributes": {"category": "Frame", "spec_value": "항공 알루미늄", "option_price": "초경량 알루미늄"}},
            {"id": "PROMO_SPRING_20", "name": "봄맞이 시즌오프 기획전 (20% 할인 쿠폰)", "type": "PromoEvent", "desc": "신학기 러닝 시즌 오픈 전상품 20% 즉시할인 및 멤버십 적립", "attributes": {"discount_rate": "20% 할인", "discount_val": "최대 7만원 할인", "period": "2025-04-30까지"}},
            {"id": "PROMO_NEW_LAUNCH", "name": "신규 런칭 기념 (사은품 양말 증정 + 1만원 할인)", "type": "PromoEvent", "desc": "신제품 론칭 기념 드라이핏 레이싱 삭스 & 1만원 즉시 할인", "attributes": {"discount_amt": "10,000원 할인", "gift": "Racing Socks & Bag"}},
            {"id": "PROMO_OUTDOOR_FEST", "name": "아웃도어 페스타 (12만원 상당 그라운드시트 증정)", "type": "PromoEvent", "desc": "텐트/쉘터 구매 시 12만원 상당 방수 그라운드시트 무료 증정", "attributes": {"benefit_val": "120,000원 상당 증정", "gift": "방수 그라운드시트"}}
        ]

        edges = [
            {"source": "SKU_PEGASUS_41", "target": "BC_NIKE_RUNNING", "relation": "BELONGS_TO", "desc": "나이키 러닝 카테고리 귀속"},
            {"source": "SKU_ALPHAFLY_3", "target": "BC_NIKE_RUNNING", "relation": "BELONGS_TO", "desc": "나이키 러닝 카테고리 귀속"},
            {"source": "SKU_VAPORFLY_3", "target": "BC_NIKE_RUNNING", "relation": "BELONGS_TO", "desc": "나이키 러닝 카테고리 귀속"},
            {"source": "SKU_DOME_TENT_4P", "target": "BC_CAMPING_TENT", "relation": "BELONGS_TO", "desc": "캠핑 텐트 카테고리 귀속"},
            {"source": "SKU_TUNNEL_SHELTER", "target": "BC_CAMPING_TENT", "relation": "BELONGS_TO", "desc": "캠핑 텐트 카테고리 귀속"},
            {"source": "SKU_PEGASUS_41", "target": "SEG_BEGINNER", "relation": "TARGETS", "desc": "초보/데일리 러너 타깃"},
            {"source": "SKU_ALPHAFLY_3", "target": "SEG_MARATHON", "relation": "TARGETS", "desc": "풀코스 마라톤 엘리트 타깃"},
            {"source": "SKU_VAPORFLY_3", "target": "SEG_MARATHON", "relation": "TARGETS", "desc": "하프/풀코스 레이싱 타깃"},
            {"source": "SKU_DOME_TENT_4P", "target": "SEG_BEGINNER", "relation": "TARGETS", "desc": "입문 패밀리 캠퍼 타깃"},
            {"source": "SKU_TUNNEL_SHELTER", "target": "SEG_MARATHON", "relation": "TARGETS", "desc": "사계절 헤비 캠퍼 타깃"},
            {"source": "SKU_PEGASUS_41", "target": "SPEC_REACTX_FOAM", "relation": "APPLIES_SPEC", "desc": "ReactX 미드솔 폼 탑재"},
            {"source": "SKU_ALPHAFLY_3", "target": "SPEC_ZOOMX_FOAM", "relation": "APPLIES_SPEC", "desc": "최고급 ZoomX 폼 풀배치"},
            {"source": "SKU_ALPHAFLY_3", "target": "SPEC_CARBON_PLATE", "relation": "APPLIES_SPEC", "desc": "풀렝스 카본 플라이플레이트 탑재"},
            {"source": "SKU_VAPORFLY_3", "target": "SPEC_ZOOMX_FOAM", "relation": "APPLIES_SPEC", "desc": "초경량 ZoomX 폼 탑재"},
            {"source": "SKU_VAPORFLY_3", "target": "SPEC_CARBON_PLATE", "relation": "APPLIES_SPEC", "desc": "카본 플레이트 반발력"},
            {"source": "SKU_DOME_TENT_4P", "target": "SPEC_WATERPROOF_3000", "relation": "APPLIES_SPEC", "desc": "3,000mm 방수 스킨"},
            {"source": "SKU_DOME_TENT_4P", "target": "SPEC_ALU_POLE", "relation": "APPLIES_SPEC", "desc": "알루미늄 7001 폴대"},
            {"source": "SKU_TUNNEL_SHELTER", "target": "SPEC_WATERPROOF_3000", "relation": "APPLIES_SPEC", "desc": "립스탑 3,000mm 방수"},
            {"source": "SKU_TUNNEL_SHELTER", "target": "SPEC_ALU_POLE", "relation": "APPLIES_SPEC", "desc": "대구경 두랄루민 프레임"},
            {"source": "BC_NIKE_RUNNING", "target": "PROMO_SPRING_20", "relation": "HAS_PROMO", "desc": "봄맞이 런페스타 20% 쿠폰"},
            {"source": "SKU_ALPHAFLY_3", "target": "PROMO_NEW_LAUNCH", "relation": "HAS_PROMO", "desc": "알파플라이 3 론칭 사은품 증정"},
            {"source": "BC_CAMPING_TENT", "target": "PROMO_OUTDOOR_FEST", "relation": "HAS_PROMO", "desc": "아웃도어 페스타 그라운드시트"}
        ]

    elif "모바일" in domain or "요금제" in domain or "telco" in domain.lower():
        # -------------------------------------------------------------
        # 도메인 3: 📱 모바일 요금제 (Telco)
        # -------------------------------------------------------------
        domain_meta = {
            "id": "telco",
            "name": "📱 모바일 요금제 (Telco)",
            "bq_dataset": "gcp-project-telco.plan_ontology.telco_plan_semantic_graph",
            "parent_type": "PlanFamily",
            "parent_label": "PlanFamily (요금제 패밀리)",
            "child_type": "PlanCode",
            "child_label": "PlanCode (세부 요금제/월정액)",
            "filter_type": "TargetUser",
            "filter_label": "가입 대상 (Target User)",
            "mkt_type": "MarketingBenefit",
            "mkt_label": "MarketingBenefit (무료혜택/환산가치)",
            "spec_type": "PlanSpec",
            "spec_label": "PlanSpec (데이터/QoS/과금)",
            "rel_belongs": "BELONGS_TO",
            "rel_filter": "TARGETS",
            "rel_mkt": "HAS_BENEFIT",
            "rel_spec": "APPLIES_PLAN_SPEC",
            "filter_param_name": "가입 대상 필터 (Target User)",
            "filter_options": ["USER_GENERAL", "USER_YOUTH", "USER_SENIOR", "ALL"],
            "filter_options_labels": {"USER_GENERAL": "일반 가입자 (General)", "USER_YOUTH": "청년 만 19~34세 (Youth)", "USER_SENIOR": "시니어 만 65세 이상 (Senior)", "ALL": "ALL (전체 연령)"},
            "presets": [
                {"label": "Preset 1: 'OTT 무료로 볼 수 있는 5G 요금제 뭐가 있어?' (무료혜택/OTT환산)", "query": "OTT 무료로 볼 수 있는 5G 요금제 뭐가 있어?", "intent": "INFO_SEARCH", "seed": "PF_5G_PREMIER", "max_hop": 2, "weight_threshold": 0.50, "filter": "USER_GENERAL"},
                {"label": "Preset 2: '5G 프리미어 슈퍼 테더링 한도랑 QoS 속도 얼마야?' (요금제 월정액/추가과금)", "query": "5G 프리미어 슈퍼 테더링 한도랑 QoS 속도 얼마야?", "intent": "PURCHASE_INTENT", "seed": "PF_5G_PREMIER", "max_hop": 2, "weight_threshold": 0.50, "filter": "USER_GENERAL"},
                {"label": "Preset 3: '청년 전용 너겟 다이렉트 무약정 혜택 알려줘' (청년할인/무약정가)", "query": "청년 전용 너겟 다이렉트 무약정 혜택 알려줘", "intent": "INFO_SEARCH", "seed": "PF_NERGET_DIRECT", "max_hop": 2, "weight_threshold": 0.50, "filter": "USER_YOUTH"},
                {"label": "Preset 4: '시니어 안심 5G 요금제 데이터 스펙 확인' (시니어 요금/보험혜택)", "query": "시니어 안심 5G 요금제 데이터 스펙 확인", "intent": "PURCHASE_INTENT", "seed": "PF_SENIOR_CARE", "max_hop": 2, "weight_threshold": 0.50, "filter": "USER_SENIOR"}
            ]
        }

        nodes = [
            {"id": "PF_5G_PREMIER", "name": "5G 프리미어 패밀리 (5G Premier)", "type": "PlanFamily", "desc": "데이터 완전 무제한 & 프리미엄 미디어 결합 요금제", "attributes": {"category": "5G Postpaid", "target_tier": "Premium"}},
            {"id": "PF_NERGET_DIRECT", "name": "너겟 다이렉트 (Nerget Direct)", "type": "PlanFamily", "desc": "2030 청년 맞춤형 무약정 온라인 다이렉트 요금제", "attributes": {"category": "Direct Online", "target_tier": "Value / Youth"}},
            {"id": "PF_SENIOR_CARE", "name": "시니어 안심 케어 (Senior Care)", "type": "PlanFamily", "desc": "만 65세 이상 어르신 전용 안심 케어 요금제", "attributes": {"category": "Senior Care", "target_tier": "Silver"}},
            {"id": "PC_PREMIER_SUPER", "name": "5G 프리미어 슈퍼 [월 115,000원]", "type": "PlanCode", "desc": "완전 무제한 데이터 + 넷플릭스/디즈니+ 팩 무료", "attributes": {"monthly_fee": "월 115,000원", "monthly_fee_num": 115000, "data": "완전 무제한", "market": "USER_GENERAL"}},
            {"id": "PC_PREMIER_PLUS", "name": "5G 프리미어 플러스 [월 105,000원]", "type": "PlanCode", "desc": "완전 무제한 데이터 + 미디어 팩 1종 무료", "attributes": {"monthly_fee": "월 105,000원", "monthly_fee_num": 105000, "data": "완전 무제한", "market": "USER_GENERAL"}},
            {"id": "PC_NERGET_YOUTH", "name": "너겟 5G 청년 무제한 [월 59,000원]", "type": "PlanCode", "desc": "만 34세 이하 전용 데이터 무제한 무약정 온라인 요금제", "attributes": {"monthly_fee": "월 59,000원", "monthly_fee_num": 59000, "data": "무제한 (QoS 5Mbps)", "market": "USER_YOUTH"}},
            {"id": "PC_SENIOR_5G", "name": "5G 시니어 49 [월 49,000원]", "type": "PlanCode", "desc": "기본 15GB + 소진 시 안심 1Mbps 무제한", "attributes": {"monthly_fee": "월 49,000원", "monthly_fee_num": 49000, "data": "15GB + QoS 1Mbps", "market": "USER_SENIOR"}},
            {"id": "USER_GENERAL", "name": "일반 가입자 (General)", "type": "TargetUser", "desc": "만 19세 이상 일반 이동통신 가입 고객", "attributes": {"code": "USER_GENERAL", "age_limit": "None"}},
            {"id": "USER_YOUTH", "name": "청년 고객군 (Youth 만 19~34세)", "type": "TargetUser", "desc": "청년 전용 추가 데이터 및 라이프 혜택 대상", "attributes": {"code": "USER_YOUTH", "age_limit": "19-34세"}},
            {"id": "USER_SENIOR", "name": "시니어 고객군 (Senior 만 65세 이상)", "type": "TargetUser", "desc": "만 65세 이상 기초연금 수급자 추가 감면 대상", "attributes": {"code": "USER_SENIOR", "age_limit": "65세 이상"}},
            {"id": "SPEC_DATA_UNLIMITED", "name": "데이터 완전무제한 (+테더링 50GB 공유)", "type": "PlanSpec", "desc": "속도 제어 없는 국내 5G 완전 무제한 데이터 제공", "attributes": {"speed": "최대 1.5Gbps", "extra_fee": "0원 (추가과금 없음)", "cap": "None"}},
            {"id": "SPEC_TETHERING_50G", "name": "테더링/쉐어링 50GB (+추가요금 無)", "type": "PlanSpec", "desc": "스마트폰 핫스팟 및 태블릿 공유 데이터 50GB 제공", "attributes": {"shared_data": "50 GB", "extra_fee": "0원 (기본포함)"}},
            {"id": "SPEC_QOS_5MBPS", "name": "기본 12GB 소진 후 5Mbps QoS (추가요금 無)", "type": "PlanSpec", "desc": "기본 데이터 소진 후에도 FHD 고화질 유튜브 재생 가능한 속도 보장", "attributes": {"qos_speed": "5 Mbps", "extra_fee": "0원 (안심제공)"}},
            {"id": "SPEC_SMART_DEVICE_FREE", "name": "스마트기기 2회선 (+월 22,000원 무료)", "type": "PlanSpec", "desc": "애플워치/갤럭시워치 및 아이패드 통신요금 100% 면제", "attributes": {"device_count": "2회선", "extra_fee": "월 22,000원 지원"}},
            {"id": "BENEFIT_OTT_PACK", "name": "넷플릭스 + 디즈니+ 무료팩 (월 24,000원 상당 혜택)", "type": "MarketingBenefit", "desc": "월 24,000원 상당 프리미엄 OTT 구독료 100% 전액 지원", "attributes": {"benefit_val": "월 24,000원 상당", "val_num": 24000, "ott_partner": "Netflix / Disney+"}},
            {"id": "BENEFIT_VIP_MEMBERSHIP", "name": "VVIP 영화 연 12회 (연 180,000원 상당)", "type": "MarketingBenefit", "desc": "CGV/메가박스 영화 무료 예매권 및 VIP 라운지 혜택", "attributes": {"benefit_val": "연 180,000원 상당", "val_num": 180000, "cinema_free": "연 12회"}},
            {"id": "BENEFIT_FAMILY_COMBO", "name": "U+ 투게더 결합할인 (회선당 최대 20,000원 할인)", "type": "MarketingBenefit", "desc": "인터넷/IPTV 결합 시 가족 구성원 요금 대폭 할인", "attributes": {"benefit_val": "최대 월 20,000원 할인", "val_num": 20000, "discount_max": "20,000원"}},
            {"id": "BENEFIT_SILVER_CARE", "name": "보이스피싱 안심 보험 (최대 300만원 무상 보상)", "type": "MarketingBenefit", "desc": "금융사기 피해 시 최대 300만원 보상 및 위치조회 서비스", "attributes": {"benefit_val": "최대 300만원 무상보상", "val_num": 3000000, "insurance": "최대 300만원 보상"}}
        ]

        edges = [
            {"source": "PC_PREMIER_SUPER", "target": "PF_5G_PREMIER", "relation": "BELONGS_TO", "desc": "5G 프리미어 패밀리 귀속"},
            {"source": "PC_PREMIER_PLUS", "target": "PF_5G_PREMIER", "relation": "BELONGS_TO", "desc": "5G 프리미어 패밀리 귀속"},
            {"source": "PC_NERGET_YOUTH", "target": "PF_NERGET_DIRECT", "relation": "BELONGS_TO", "desc": "너겟 다이렉트 패밀리 귀속"},
            {"source": "PC_SENIOR_5G", "target": "PF_SENIOR_CARE", "relation": "BELONGS_TO", "desc": "시니어 안심 패밀리 귀속"},
            {"source": "PC_PREMIER_SUPER", "target": "USER_GENERAL", "relation": "TARGETS", "desc": "일반 가입자 대상"},
            {"source": "PC_PREMIER_PLUS", "target": "USER_GENERAL", "relation": "TARGETS", "desc": "일반 가입자 대상"},
            {"source": "PC_NERGET_YOUTH", "target": "USER_YOUTH", "relation": "TARGETS", "desc": "청년층 전용 요금제"},
            {"source": "PC_SENIOR_5G", "target": "USER_SENIOR", "relation": "TARGETS", "desc": "시니어 어르신 전용 요금제"},
            {"source": "PC_PREMIER_SUPER", "target": "SPEC_DATA_UNLIMITED", "relation": "APPLIES_PLAN_SPEC", "desc": "완전 무제한 데이터 제공"},
            {"source": "PC_PREMIER_SUPER", "target": "SPEC_TETHERING_50G", "relation": "APPLIES_PLAN_SPEC", "desc": "테더링 50GB 전용 제공"},
            {"source": "PC_PREMIER_SUPER", "target": "SPEC_SMART_DEVICE_FREE", "relation": "APPLIES_PLAN_SPEC", "desc": "스마트기기 2회선 무료"},
            {"source": "PC_PREMIER_PLUS", "target": "SPEC_DATA_UNLIMITED", "relation": "APPLIES_PLAN_SPEC", "desc": "완전 무제한 데이터 제공"},
            {"source": "PC_NERGET_YOUTH", "target": "SPEC_QOS_5MBPS", "relation": "APPLIES_PLAN_SPEC", "desc": "안심 QoS 5Mbps 무제한"},
            {"source": "PF_5G_PREMIER", "target": "BENEFIT_OTT_PACK", "relation": "HAS_BENEFIT", "desc": "OTT 무료 구독팩"},
            {"source": "PF_5G_PREMIER", "target": "BENEFIT_VIP_MEMBERSHIP", "relation": "HAS_BENEFIT", "desc": "VIP 영화 멤버십"},
            {"source": "PF_5G_PREMIER", "target": "BENEFIT_FAMILY_COMBO", "relation": "HAS_BENEFIT", "desc": "가족 유무선 결합할인"},
            {"source": "PF_SENIOR_CARE", "target": "BENEFIT_SILVER_CARE", "relation": "HAS_BENEFIT", "desc": "금융사기 안심 보상 보험"}
        ]

    else:
        # -------------------------------------------------------------
        # 도메인 4: 🔬 반도체 8대 공정 (Semiconductor / Fab Recipe Impact)
        # -------------------------------------------------------------
        domain_meta = {
            "id": "semiconductor",
            "name": "🔬 반도체 8대 공정 (Semiconductor)",
            "bq_dataset": "gcp-project-semicon.fab_ontology.semiconductor_process_graph",
            "parent_type": "ProcessStage",
            "parent_label": "ProcessStage (8대 제조공정)",
            "child_type": "RecipeParam",
            "child_label": "RecipeParam (공정 레시피/조건)",
            "filter_type": "FabLine",
            "filter_label": "생산 팹/라인 (Fab Line)",
            "mkt_type": "YieldImpact",
            "mkt_label": "YieldImpact (수율/결함 영향도)",
            "spec_type": "EquipmentSpec",
            "spec_label": "EquipmentSpec (설비/챔버 스펙)",
            "rel_belongs": "BELONGS_TO",
            "rel_filter": "RUNS_ON",
            "rel_mkt": "AFFECTS_YIELD",
            "rel_spec": "CONTROLS_EQUIPMENT",
            "filter_param_name": "생산 팹/라인 필터 (Fab Line Constraint)",
            "filter_options": ["FAB_P3_DRAM", "FAB_P4_NAND", "FAB_S5_FOUNDRY", "ALL"],
            "filter_options_labels": {
                "FAB_P3_DRAM": "평택 P3 (1b nm DRAM 라인)",
                "FAB_P4_NAND": "평택 P4 (V9 300+단 NAND 라인)",
                "FAB_S5_FOUNDRY": "화성 S5 (SF3 3nm GAA 파운드리)",
                "ALL": "ALL (전체 팹 라인)"
            },
            "presets": [
                {
                    "label": "Preset 1: 'EUV 노광량(Dose) 45mJ 상향 시 수율 및 결함 영향도' (수율 영향 분석)",
                    "query": "EUV 노광량(Dose) 45mJ 상향 시 수율 및 결함 영향도",
                    "intent": "INFO_SEARCH",
                    "seed": "PROC_PHOTO",
                    "max_hop": 2,
                    "weight_threshold": 0.50,
                    "filter": "FAB_P3_DRAM"
                },
                {
                    "label": "Preset 2: 'EUV 노광기 파장 및 펠리클 투과율 장비 제어 스펙' (설비/레시피 제어)",
                    "query": "EUV 노광기 파장 및 펠리클 투과율 장비 제어 스펙",
                    "intent": "PURCHASE_INTENT",
                    "seed": "PROC_PHOTO",
                    "max_hop": 2,
                    "weight_threshold": 0.50,
                    "filter": "FAB_P3_DRAM"
                },
                {
                    "label": "Preset 3: 'V9 NAND 300단 HARC 고선택비 에칭 시 홀 휨/불량 분석' (수율 영향 분석)",
                    "query": "V9 NAND 300단 HARC 고선택비 에칭 시 홀 휨/불량 분석",
                    "intent": "INFO_SEARCH",
                    "seed": "PROC_ETCH",
                    "max_hop": 2,
                    "weight_threshold": 0.50,
                    "filter": "FAB_P4_NAND"
                },
                {
                    "label": "Preset 4: '3nm GAA High-K ALD 박막 증착온도 280℃ 변경 장비 스펙' (설비/레시피 제어)",
                    "query": "3nm GAA High-K ALD 박막 증착온도 280℃ 변경 장비 스펙",
                    "intent": "PURCHASE_INTENT",
                    "seed": "PROC_DEPO",
                    "max_hop": 2,
                    "weight_threshold": 0.50,
                    "filter": "FAB_S5_FOUNDRY"
                }
            ]
        }

        nodes = [
            {"id": "PROC_PHOTO", "name": "03. 포토/노광 공정 (Photolithography)", "type": "ProcessStage", "desc": "EUV 13.5nm 극자외선 기반 초미세 회로 패턴 형성 공정", "attributes": {"stage_no": "03", "tech_node": "1b nm / 3nm GAA", "key_metric": "CD Uniformity & Overlay"}},
            {"id": "PROC_ETCH", "name": "04. 식각 공정 (Plasma Dry Etching)", "type": "ProcessStage", "desc": "HARC(High Aspect Ratio Contact) 고선택비 플라즈마 건식 식각 공정", "attributes": {"stage_no": "04", "tech_node": "V9 300+단 NAND", "key_metric": "Selectivity & Tilt Angle"}},
            {"id": "PROC_DEPO", "name": "05. 박막 증착 공정 (ALD / Thin Film)", "type": "ProcessStage", "desc": "원자층 단위 정밀 두께 제어 High-K 유전막 및 메탈 게이트 증착", "attributes": {"stage_no": "05", "tech_node": "3nm GAA MBCFET", "key_metric": "Step Coverage & Breakdown Voltage"}},
            {"id": "PROC_CLEAN", "name": "02/06. 세정 및 이온주입 (Clean & Ion Implant)", "type": "ProcessStage", "desc": "초순수 RCA/초임계 CO2 세정 및 채널 도핑 이온주입 공정", "attributes": {"stage_no": "02/06", "tech_node": "1b nm DRAM", "key_metric": "Particle Count & Doping Depth"}},
            {"id": "RCP_EUV_DOSE_45", "name": "EUV Dose 노광량 45mJ/cm² [+12% 상향] [웨이퍼당 비용 +$4.20]", "type": "RecipeParam", "desc": "EUV 광원 에너지 노광량을 40mJ에서 45mJ로 상향하여 패턴 붕괴(LWR) 방지", "attributes": {"param_name": "Exposure Dose", "target_val": "45 mJ/cm²", "cost_impact": "+$4.20/wafer", "market": "FAB_P3_DRAM"}},
            {"id": "RCP_EUV_FOCUS_OFFSET", "name": "EUV 포커스 오프셋 -5nm [초점 미세조정] [비용 $0]", "type": "RecipeParam", "desc": "웨이퍼 단차 극복을 위한 Depth of Focus(DoF) 최적화", "attributes": {"param_name": "Focus Offset", "target_val": "-5 nm", "cost_impact": "$0", "market": "FAB_P3_DRAM"}},
            {"id": "RCP_ETCH_CRYO_60", "name": "극저온 -60℃ 플라즈마 식각 [+C4F8 유량비 1.25] [챔버가동비 +$8.50]", "type": "RecipeParam", "desc": "극저온 에칭으로 300단 초고종횡비 채널 홀 식각 속도 및 수직도 향상", "attributes": {"param_name": "Chamber Temp & Gas Ratio", "target_val": "-60℃ / C4F8:CF4=1.25", "cost_impact": "+$8.50/wafer", "market": "FAB_P4_NAND"}},
            {"id": "RCP_ETCH_RF_POWER", "name": "식각 Dual RF Source 3,200W [+400W 파워 업] [전력비 +$1.80]", "type": "RecipeParam", "desc": "플라즈마 이온 에너지 밀도 강화로 하부 바닥 도달 식각율 극대화", "attributes": {"param_name": "Source RF Power", "target_val": "3,200 W", "cost_impact": "+$1.80/wafer", "market": "FAB_P4_NAND"}},
            {"id": "RCP_ALD_HIGHK_280", "name": "High-K ALD 증착온도 280℃ [+20℃ 상향] [원자층 제어 $0]", "type": "RecipeParam", "desc": "GAA 나노시트 게이트 산화막 누설전류 차단 및 치밀도 강화", "attributes": {"param_name": "Deposition Temp", "target_val": "280 ℃ (HZO Film)", "cost_impact": "$0 (Tuning)", "market": "FAB_S5_FOUNDRY"}},
            {"id": "RCP_CLEAN_SCCO2", "name": "초임계 CO2 건조 세정 [패턴붕괴 방지] [특수가스비 +$3.10]", "type": "RecipeParam", "desc": "표면장력 Zero 초임계 유체로 1b nm 초미세 패턴 쓰러짐 완벽 방지", "attributes": {"param_name": "Drying Method", "target_val": "Supercritical CO2 (73.8bar, 31.1℃)", "cost_impact": "+$3.10/wafer", "market": "FAB_P3_DRAM"}},
            {"id": "FAB_P3_DRAM", "name": "평택 P3 (1b nm DRAM 생산라인)", "type": "FabLine", "desc": "12나노급 1b nm EUV 5개 레이어 적용 첨단 D램 양산 팹", "attributes": {"code": "FAB_P3_DRAM", "site": "Pyeongtaek Campus", "cleanroom": "Class 1", "capacity": "150k wpm"}},
            {"id": "FAB_P4_NAND", "name": "평택 P4 (V9 300+단 NAND 생산라인)", "type": "FabLine", "desc": "300단 이상 더블 스택 HARC 에칭 적용 초고용량 V-NAND 팹", "attributes": {"code": "FAB_P4_NAND", "site": "Pyeongtaek Campus", "cleanroom": "Class 1", "capacity": "120k wpm"}},
            {"id": "FAB_S5_FOUNDRY", "name": "화성 S5 (SF3 3nm GAA 파운드리 라인)", "type": "FabLine", "desc": "MBCFET GAA(Gate-All-Around) 3세대 차세대 시스템반도체 팹", "attributes": {"code": "FAB_S5_FOUNDRY", "site": "Hwaseong Campus", "cleanroom": "Class 0.1", "capacity": "45k wpm"}},
            {"id": "YIELD_DEFECT_REDUCE", "name": "마이크로 브릿지 결함률 18% 감소 [연 180억원 절감]", "type": "YieldImpact", "desc": "EUV 노광량 최적화로 라인 에지 러프니스(LER) 및 쇼트 불량 획기적 억제", "attributes": {"defect_reduction": "-18.4%", "annual_savings": "180억원", "yield_gain": "+1.8%p"}},
            {"id": "YIELD_HOLE_TILT_FIX", "name": "HARC 에칭 틸트 불량 제로화 [수율 +3.2%p 향상]", "type": "YieldImpact", "desc": "극저온 플라즈마 제어로 300단 채널 홀 기울어짐 및 벤딩 결함 완벽 차단", "attributes": {"tilt_angle": "< 0.1 deg", "yield_gain": "+3.2%p", "economic_value": "연 260억원"}},
            {"id": "YIELD_LEAKAGE_SUPPRESS", "name": "GAA 게이트 누설전류 35% 차단 [소비전력 -12%]", "type": "YieldImpact", "desc": "High-K 박막 치밀도 증가로 오프스테이트 누설전류 억제 및 수명 2배 증대", "attributes": {"leakage_reduction": "-35.2%", "power_saving": "-12.0%", "reliability": "10-Year MTBF"}},
            {"id": "YIELD_PATTERN_COLLAPSE", "name": "1b nm 커패시터 패턴 붕괴 불량 제로 [수율 +2.5%p]", "type": "YieldImpact", "desc": "초임계 CO2 건조 적용으로 모세관 현상에 의한 미세 기둥 쓰러짐 방지", "attributes": {"collapse_rate": "0.00 ppm", "yield_gain": "+2.5%p", "cost_avoidance": "연 140억원"}},
            {"id": "EQ_ASML_NXE3800", "name": "ASML Twinscan NXE:3800F EUV [장비가 $220M] (+900W 광원)", "type": "EquipmentSpec", "desc": "0.33 NA, 시간당 220매(WPH) 고생산성 High-Dose 극자외선 노광 시스템", "attributes": {"vendor": "ASML", "wavelength": "13.5 nm", "eq_price": "$220M", "throughput": "220 WPH"}},
            {"id": "EQ_PELLICLE_CNT", "name": "Carbon Nanotube EUV 펠리클 (+투과율 92%)", "type": "EquipmentSpec", "desc": "EUV 고출력(600W+) 광원 열변형 방지 및 92% 이상 고투과율 탄소나노튜브 펠리클", "attributes": {"type": "CNT Pellicle", "transmittance": "92.4%", "heat_limit": "800 W"}},
            {"id": "EQ_LAM_CRYO_ETCHER", "name": "Lam Research 극저온 유전체 식각 챔버 (+동기화 RF)", "type": "EquipmentSpec", "desc": "극저온 -70℃ 냉각 정전척(ESC) 및 초고주파 Dual RF 펄스 제어 챔버", "attributes": {"vendor": "Lam Research", "temp_range": "-70℃ ~ +60℃", "rf_frequency": "60MHz/2MHz Dual"}},
            {"id": "EQ_TEL_INDY_ALD", "name": "TEL Certas LEAGEND High-K ALD [초정밀 0.1Å 제어]", "type": "EquipmentSpec", "desc": "3D GAA MBCFET 다층 채널 틈새 100% 균일 Conformal 원자층 증착 장비", "attributes": {"vendor": "Tokyo Electron (TEL)", "step_coverage": "99.8%", "film_uniformity": "< 0.5%"}}
        ]

        edges = [
            {"source": "RCP_EUV_DOSE_45", "target": "PROC_PHOTO", "relation": "BELONGS_TO", "desc": "포토/노광 공정 소속"},
            {"source": "RCP_EUV_FOCUS_OFFSET", "target": "PROC_PHOTO", "relation": "BELONGS_TO", "desc": "포토/노광 공정 소속"},
            {"source": "RCP_ETCH_CRYO_60", "target": "PROC_ETCH", "relation": "BELONGS_TO", "desc": "플라즈마 식각 공정 소속"},
            {"source": "RCP_ETCH_RF_POWER", "target": "PROC_ETCH", "relation": "BELONGS_TO", "desc": "플라즈마 식각 공정 소속"},
            {"source": "RCP_ALD_HIGHK_280", "target": "PROC_DEPO", "relation": "BELONGS_TO", "desc": "박막 증착 공정 소속"},
            {"source": "RCP_CLEAN_SCCO2", "target": "PROC_CLEAN", "relation": "BELONGS_TO", "desc": "세정 공정 소속"},
            {"source": "RCP_EUV_DOSE_45", "target": "FAB_P3_DRAM", "relation": "RUNS_ON", "desc": "평택 P3 DRAM 라인 적용"},
            {"source": "RCP_EUV_FOCUS_OFFSET", "target": "FAB_P3_DRAM", "relation": "RUNS_ON", "desc": "평택 P3 DRAM 라인 적용"},
            {"source": "RCP_ETCH_CRYO_60", "target": "FAB_P4_NAND", "relation": "RUNS_ON", "desc": "평택 P4 NAND 라인 적용"},
            {"source": "RCP_ETCH_RF_POWER", "target": "FAB_P4_NAND", "relation": "RUNS_ON", "desc": "평택 P4 NAND 라인 적용"},
            {"source": "RCP_ALD_HIGHK_280", "target": "FAB_S5_FOUNDRY", "relation": "RUNS_ON", "desc": "화성 S5 3nm 파운드리 적용"},
            {"source": "RCP_CLEAN_SCCO2", "target": "FAB_P3_DRAM", "relation": "RUNS_ON", "desc": "평택 P3 DRAM 라인 적용"},
            {"source": "RCP_EUV_DOSE_45", "target": "EQ_ASML_NXE3800", "relation": "CONTROLS_EQUIPMENT", "desc": "ASML EUV 노광기 파라미터 제어"},
            {"source": "RCP_EUV_DOSE_45", "target": "EQ_PELLICLE_CNT", "relation": "CONTROLS_EQUIPMENT", "desc": "CNT 펠리클 투과율 제어"},
            {"source": "RCP_ETCH_CRYO_60", "target": "EQ_LAM_CRYO_ETCHER", "relation": "CONTROLS_EQUIPMENT", "desc": "Lam 극저온 에칭 챔버 제어"},
            {"source": "RCP_ALD_HIGHK_280", "target": "EQ_TEL_INDY_ALD", "relation": "CONTROLS_EQUIPMENT", "desc": "TEL High-K ALD 챔버 제어"},
            {"source": "PROC_PHOTO", "target": "YIELD_DEFECT_REDUCE", "relation": "AFFECTS_YIELD", "desc": "EUV 노광 불량 억제 및 수율 개선"},
            {"source": "PROC_ETCH", "target": "YIELD_HOLE_TILT_FIX", "relation": "AFFECTS_YIELD", "desc": "300단 HARC 틸트 결함 제로화"},
            {"source": "PROC_DEPO", "target": "YIELD_LEAKAGE_SUPPRESS", "relation": "AFFECTS_YIELD", "desc": "3nm GAA 누설전류 억제"},
            {"source": "PROC_CLEAN", "target": "YIELD_PATTERN_COLLAPSE", "relation": "AFFECTS_YIELD", "desc": "초임계 세정 패턴 붕괴 방지"}
        ]

    return nodes, edges, domain_meta


def get_native_tables(domain: str) -> dict:
    """
    선택된 비즈니스 도메인에 대한 BigQuery 원본 관계형 테이블(Relational Tables) Mock 데이터를 반환합니다.
    """
    if "자동차" in domain or "automotive" in domain.lower():
        return {
            "dim_family_car (차종 마스터)": pd.DataFrame([
                {"family_id": "FC_SORENTO", "family_name": "소렌토 (Sorento)", "brand": "Kia", "segment": "Midsize SUV", "seats": "5/6/7인승", "origin": "KR"},
                {"family_id": "FC_SANTAFE", "family_name": "싼타페 (Santa Fe)", "brand": "Hyundai", "segment": "Midsize SUV", "seats": "5/6/7인승", "origin": "KR"}
            ]),
            "dim_model_code (모델코드 마스터)": pd.DataFrame([
                {"model_id": "MC_MQ4_KR", "family_id": "FC_SORENTO", "model_code": "MQ4", "base_price": 35000000, "base_price_formatted": "3,500만원~", "powertrain": "2.5T / 2.2D", "market": "KR", "launch_year": 2024},
                {"model_id": "MC_MQ4_HEV_KR", "family_id": "FC_SORENTO", "model_code": "MQ4 HEV", "base_price": 37800000, "base_price_formatted": "3,780만원~", "powertrain": "1.6T HEV", "market": "KR", "launch_year": 2024},
                {"model_id": "MC_MQ4_US", "family_id": "FC_SORENTO", "model_code": "MQ4a", "base_price": 31990, "base_price_formatted": "$31,990~", "powertrain": "2.5T / 1.6T HEV", "market": "US", "launch_year": 2024},
                {"model_id": "MC_MX5_KR", "family_id": "FC_SANTAFE", "model_code": "MX5", "base_price": 35400000, "base_price_formatted": "3,540만원~", "powertrain": "2.5T", "market": "KR", "launch_year": 2024},
                {"model_id": "MC_MX5_HEV_KR", "family_id": "FC_SANTAFE", "model_code": "MX5 HEV", "base_price": 38800000, "base_price_formatted": "3,880만원~", "powertrain": "1.6T HEV", "market": "KR", "launch_year": 2024},
                {"model_id": "MC_MX5_US", "family_id": "FC_SANTAFE", "model_code": "MX5a", "base_price": 33950, "base_price_formatted": "$33,950~", "powertrain": "2.5T AWD", "market": "US", "launch_year": 2024}
            ]),
            "dim_region_market (판매지역 마스터)": pd.DataFrame([
                {"region_id": "REG_KR", "region_code": "KR", "region_name": "대한민국 내수", "currency": "KRW", "ev_subsidy": "적용", "emission_std": "K-ULEV"},
                {"region_id": "REG_US", "region_code": "US", "region_name": "미국 북미시장", "currency": "USD", "ev_subsidy": "IRA 대상", "emission_std": "EPA Tier 3"},
                {"region_id": "REG_SEA", "region_code": "SEA", "region_name": "동남아 아세안", "currency": "USD/Local", "ev_subsidy": "일부적용", "emission_std": "Euro 5"}
            ]),
            "dim_spec_item (옵션/사양 마스터)": pd.DataFrame([
                {"spec_id": "SPEC_HEV_16T", "spec_name": "1.6T HEV 전용 엔진", "option_price": "0원 (기본포함)", "category": "Powertrain", "spec_details": "245ps 합산 / 15.7km/L"},
                {"spec_id": "SPEC_DRIVEWISE", "spec_name": "드라이브 와이즈 ADAS", "option_price": "120만원", "category": "Safety / ADAS", "spec_details": "HDA2 + 전방 충돌방지"},
                {"spec_id": "SPEC_AWD", "spec_name": "전자식 AWD 4륜구동", "option_price": "200만원", "category": "Drivetrain", "spec_details": "터레인 모드 연동 4WD"},
                {"spec_id": "SPEC_HUD", "spec_name": "10인치 헤드업 디스플레이", "option_price": "70만원", "category": "Convenience", "spec_details": "윈드실드 타입 고해상도 HUD"},
                {"spec_id": "SPEC_BUILTINCAM2", "spec_name": "QHD 빌트인 캠 2", "option_price": "45만원", "category": "Electronics", "spec_details": "전후방 QHD 녹화 & 음성녹음"},
                {"spec_id": "SPEC_GAS_25T", "spec_name": "2.5T 가솔린 AWD", "option_price": "$2,000", "category": "Powertrain", "spec_details": "281ps 스마트스트림 G2.5T"}
            ]),
            "rel_model_region (모델-지역 매핑 테이블)": pd.DataFrame([
                {"model_id": "MC_MQ4_KR", "region_id": "REG_KR", "is_primary_market": True, "base_price": "35,000,000 KRW", "warranty": "5년 / 10만km"},
                {"model_id": "MC_MQ4_HEV_KR", "region_id": "REG_KR", "is_primary_market": True, "base_price": "37,800,000 KRW", "warranty": "하이브리드 10년 / 20만km"},
                {"model_id": "MC_MQ4_US", "region_id": "REG_US", "is_primary_market": True, "base_price": "$31,990 USD", "warranty": "10-Year / 100k Miles"},
                {"model_id": "MC_MX5_KR", "region_id": "REG_KR", "is_primary_market": True, "base_price": "35,400,000 KRW", "warranty": "5년 / 10만km"},
                {"model_id": "MC_MX5_HEV_KR", "region_id": "REG_KR", "is_primary_market": True, "base_price": "38,800,000 KRW", "warranty": "하이브리드 10년 / 20만km"},
                {"model_id": "MC_MX5_US", "region_id": "REG_US", "is_primary_market": True, "base_price": "$33,950 USD", "warranty": "10-Year / 100k Miles"}
            ]),
            "rel_family_marketing (차종-마케팅/KSP 매핑 테이블)": pd.DataFrame([
                {"family_id": "FC_SORENTO", "mkt_id": "MKT_2025_RELEASE", "ksp_title": "2025 페이스리프트 (신형 출시)", "discount_benefit": "50만원 바우처", "content": "연 2.9% 저금리 할부 & 50만원 바우처", "weight_info": 0.1, "weight_purchase": 0.9},
                {"family_id": "FC_SORENTO", "mkt_id": "MKT_FAMILY_SPACE", "ksp_title": "동급 최고 패밀리 SUV 공간성", "discount_benefit": "2열 독립시트 무상", "content": "2,815mm 휠베이스 & 캡틴시트 무상 업그레이드", "weight_info": 0.1, "weight_purchase": 0.9},
                {"family_id": "FC_SORENTO", "mkt_id": "MKT_DESIGN_STARMAP", "ksp_title": "시그니처 스타맵 라이팅 디자인", "discount_benefit": "30만원 할인", "content": "스타일 패키지 30만 할인 지원", "weight_info": 0.1, "weight_purchase": 0.9},
                {"family_id": "FC_SANTAFE", "mkt_id": "MKT_SANTAFE_HLIGHT", "ksp_title": "H-라이트 디자인 & 테라스 테일게이트", "discount_benefit": "40만원 상당 지원", "content": "아웃도어 특화 패키지 40만원 지원", "weight_info": 0.1, "weight_purchase": 0.9},
                {"family_id": "FC_SANTAFE", "mkt_id": "MKT_FAMILY_SPACE", "ksp_title": "3열 독립 시트 & 대형 실내공간", "discount_benefit": "차박 매트 증정", "content": "2,044L 트렁크 공간 및 평탄화 차박 지원", "weight_info": 0.1, "weight_purchase": 0.9}
            ])
        }
    elif "이커머스" in domain or "ecommerce" in domain.lower():
        return {
            "dim_brand_category (카테고리 마스터)": pd.DataFrame([
                {"category_id": "BC_NIKE_RUNNING", "brand_name": "Nike", "category_name": "퍼포먼스 러닝화 라인업", "season": "2025 S/S", "target_sports": "Running / Marathon"},
                {"category_id": "BC_CAMPING_TENT", "brand_name": "SnowPeak / Helinox", "category_name": "사계절 패밀리 캠핑 텐트/쉘터", "season": "2025 S/S", "target_sports": "Camping / Outdoor"}
            ]),
            "dim_product_sku (상품 SKU 마스터)": pd.DataFrame([
                {"sku_id": "SKU_PEGASUS_41", "category_id": "BC_NIKE_RUNNING", "sku_code": "FD2722-100", "product_name": "나이키 페가수스 41", "price": 159000, "price_formatted": "159,000원", "weight_g": 281, "target_segment": "SEG_BEGINNER"},
                {"sku_id": "SKU_ALPHAFLY_3", "category_id": "BC_NIKE_RUNNING", "sku_code": "FD8311-700", "product_name": "에어줌 알파플라이 3", "price": 359000, "price_formatted": "359,000원", "weight_g": 218, "target_segment": "SEG_MARATHON"},
                {"sku_id": "SKU_VAPORFLY_3", "category_id": "BC_NIKE_RUNNING", "sku_code": "DV4129-100", "product_name": "줌엑스 베이퍼플라이 3", "price": 299000, "price_formatted": "299,000원", "weight_g": 198, "target_segment": "SEG_MARATHON"},
                {"sku_id": "SKU_DOME_TENT_4P", "category_id": "BC_CAMPING_TENT", "sku_code": "SDE-001RH", "product_name": "어메니티 돔 4인용 텐트", "price": 498000, "price_formatted": "498,000원", "capacity": "4인용", "target_segment": "SEG_BEGINNER"},
                {"sku_id": "SKU_TUNNEL_SHELTER", "category_id": "BC_CAMPING_TENT", "sku_code": "TP-671R", "product_name": "랜드락 대형 투룸 쉘터", "price": 1980000, "price_formatted": "1,980,000원", "capacity": "6인용", "target_segment": "SEG_MARATHON"}
            ]),
            "dim_product_spec (상품 스펙 마스터)": pd.DataFrame([
                {"spec_id": "SPEC_ZOOMX_FOAM", "spec_name": "ZoomX 고반발 폼", "spec_value": "기본탑재 (반발력 85%)", "option_price": "핵심 기본탑재", "category": "Midsole"},
                {"spec_id": "SPEC_CARBON_PLATE", "spec_name": "풀렝스 카본 플라이플레이트", "spec_value": "선수용옵션 (카본 100%)", "option_price": "프리미엄 옵션", "category": "Plate"},
                {"spec_id": "SPEC_REACTX_FOAM", "spec_name": "ReactX 친환경 폼", "spec_value": "기본탑재 (쿠셔닝 +13%)", "option_price": "친환경 기본사양", "category": "Midsole"},
                {"spec_id": "SPEC_WATERPROOF_3000", "spec_name": "내수압 3,000mm 립스탑", "spec_value": "테프론 발수 코팅", "option_price": "고급 원단사양", "category": "Fabric"},
                {"spec_id": "SPEC_ALU_POLE", "spec_name": "두랄루민 7001 폴대", "spec_value": "항공기용 알루미늄", "option_price": "초경량 고강도", "category": "Frame"}
            ]),
            "rel_category_promo (카테고리-프로모션 매핑 테이블)": pd.DataFrame([
                {"category_id": "BC_NIKE_RUNNING", "promo_id": "PROMO_SPRING_20", "promo_title": "봄맞이 시즌오프 기획전", "discount_rate": "20% 할인 쿠폰", "discount_val": "최대 7만원 할인", "period": "2025-04-30까지", "weight_info": 0.1, "weight_purchase": 0.9},
                {"category_id": "BC_NIKE_RUNNING", "promo_id": "PROMO_NEW_LAUNCH", "promo_title": "신규 런칭 기념 프로모션", "discount_rate": "사은품 증정 + 1만원 할인", "discount_val": "10,000원 할인", "period": "재고 소진 시까지", "weight_info": 0.1, "weight_purchase": 0.9},
                {"category_id": "BC_CAMPING_TENT", "promo_id": "PROMO_OUTDOOR_FEST", "promo_title": "아웃도어 페스타 증정 행사", "discount_rate": "그라운드시트 증정", "discount_val": "120,000원 상당 증정", "period": "2025-05-31까지", "weight_info": 0.1, "weight_purchase": 0.9}
            ])
        }
    elif "모바일" in domain or "요금제" in domain or "telco" in domain.lower():
        return {
            "dim_plan_family (요금제 패밀리 마스터)": pd.DataFrame([
                {"family_id": "PF_5G_PREMIER", "family_name": "5G 프리미어 패밀리", "network_type": "5G Postpaid", "target_tier": "Premium", "voice_sms": "기본 무제한"},
                {"family_id": "PF_NERGET_DIRECT", "family_name": "너겟 다이렉트", "network_type": "5G Direct Online", "target_tier": "Value / Youth", "voice_sms": "기본 무제한"},
                {"family_id": "PF_SENIOR_CARE", "family_name": "시니어 안심 케어", "network_type": "5G Silver Care", "target_tier": "Silver", "voice_sms": "기본 무제한"}
            ]),
            "dim_plan_code (요금제 코드 마스터)": pd.DataFrame([
                {"plan_id": "PC_PREMIER_SUPER", "family_id": "PF_5G_PREMIER", "plan_code": "PLAN_5G_PSUPER", "plan_name": "5G 프리미어 슈퍼", "monthly_fee": 115000, "monthly_fee_formatted": "월 115,000원", "target_user": "USER_GENERAL"},
                {"plan_id": "PC_PREMIER_PLUS", "family_id": "PF_5G_PREMIER", "plan_code": "PLAN_5G_PPLUS", "plan_name": "5G 프리미어 플러스", "monthly_fee": 105000, "monthly_fee_formatted": "월 105,000원", "target_user": "USER_GENERAL"},
                {"plan_id": "PC_NERGET_YOUTH", "family_id": "PF_NERGET_DIRECT", "plan_code": "PLAN_NERGET_YOUTH", "plan_name": "너겟 5G 청년 무제한", "monthly_fee": 59000, "monthly_fee_formatted": "월 59,000원", "target_user": "USER_YOUTH"},
                {"plan_id": "PC_SENIOR_5G", "family_id": "PF_SENIOR_CARE", "plan_code": "PLAN_SENIOR_49", "plan_name": "5G 시니어 49", "monthly_fee": 49000, "monthly_fee_formatted": "월 49,000원", "target_user": "USER_SENIOR"}
            ]),
            "dim_plan_spec (요금제 스펙 마스터)": pd.DataFrame([
                {"spec_id": "SPEC_DATA_UNLIMITED", "spec_name": "데이터 완전무제한", "extra_fee": "0원 (무제한)", "data_allowance": "완전 무제한 (No Cap)", "qos_speed": "속도 제한 없음"},
                {"spec_id": "SPEC_TETHERING_50G", "spec_name": "테더링/쉐어링 50GB", "extra_fee": "0원 (기본제공)", "data_allowance": "50 GB 별도제공", "qos_speed": "소진 시 5Mbps"},
                {"spec_id": "SPEC_QOS_5MBPS", "spec_name": "기본 소진 후 5Mbps QoS", "extra_fee": "0원 (추가과금 無)", "data_allowance": "12GB 기본", "qos_speed": "5 Mbps 안심 무제한 (FHD 가능)"},
                {"spec_id": "SPEC_SMART_DEVICE_FREE", "spec_name": "스마트기기 2회선 무료", "extra_fee": "월 22,000원 지원", "data_allowance": "스마트워치/패드 2회선", "qos_speed": "본회선 공유"}
            ]),
            "rel_plan_benefit (요금제-부가 혜택/멤버십 매핑 테이블)": pd.DataFrame([
                {"plan_id": "PF_5G_PREMIER", "benefit_id": "BENEFIT_OTT_PACK", "benefit_name": "넷플릭스 + 디즈니+ 무료팩", "monthly_value": "월 24,000원 상당 혜택", "ott_partner": "Netflix / Disney+", "weight_info": 0.1, "weight_purchase": 0.9},
                {"plan_id": "PF_5G_PREMIER", "benefit_id": "BENEFIT_VIP_MEMBERSHIP", "benefit_name": "VVIP 영화 연 12회 무료", "monthly_value": "연 180,000원 상당", "ott_partner": "CGV / Megabox", "weight_info": 0.1, "weight_purchase": 0.9},
                {"plan_id": "PF_5G_PREMIER", "benefit_id": "BENEFIT_FAMILY_COMBO", "benefit_name": "U+ 투게더 결합할인", "monthly_value": "회선당 최대 20,000원 할인", "ott_partner": "가족 결합", "weight_info": 0.1, "weight_purchase": 0.9},
                {"plan_id": "PF_SENIOR_CARE", "benefit_id": "BENEFIT_SILVER_CARE", "benefit_name": "보이스피싱 안심 보험", "monthly_value": "최대 300만원 무상 보상", "ott_partner": "KB손해보험", "weight_info": 0.1, "weight_purchase": 0.9}
            ])
        }
    else:
        return {
            "dim_process_stage (8대 제조공정 마스터)": pd.DataFrame([
                {"process_id": "PROC_PHOTO", "stage_no": "03", "process_name": "포토/노광 공정 (Photolithography)", "tech_node": "1b nm / 3nm GAA", "key_metric": "CD Uniformity & Overlay", "fab_floor": "Cleanroom Bay 3F"},
                {"process_id": "PROC_ETCH", "stage_no": "04", "process_name": "식각 공정 (Plasma Dry Etching)", "tech_node": "V9 300+단 NAND", "key_metric": "Selectivity & Tilt Angle", "fab_floor": "Cleanroom Bay 2F"},
                {"process_id": "PROC_DEPO", "stage_no": "05", "process_name": "박막 증착 공정 (ALD / Thin Film)", "tech_node": "3nm GAA MBCFET", "key_metric": "Step Coverage & Breakdown", "fab_floor": "Cleanroom Bay 2F"},
                {"process_id": "PROC_CLEAN", "stage_no": "02/06", "process_name": "세정 및 이온주입 (Clean & Implant)", "tech_node": "1b nm DRAM", "key_metric": "Particle Count (<0.01/cm²)", "fab_floor": "Cleanroom Bay 1F"}
            ]),
            "dim_recipe_param (공정 레시피/조건 마스터)": pd.DataFrame([
                {"recipe_id": "RCP_EUV_DOSE_45", "process_id": "PROC_PHOTO", "recipe_code": "RCP_PHOTO_DOSE_45M", "param_name": "EUV 노광량 (Exposure Dose)", "target_value": "45 mJ/cm²", "cost_impact": "+$4.20/wafer", "market_fab": "FAB_P3_DRAM"},
                {"recipe_id": "RCP_EUV_FOCUS_OFFSET", "process_id": "PROC_PHOTO", "recipe_code": "RCP_PHOTO_FOCUS_N5", "param_name": "초점 오프셋 (Focus Offset)", "target_value": "-5 nm", "cost_impact": "$0/wafer", "market_fab": "FAB_P3_DRAM"},
                {"recipe_id": "RCP_ETCH_CRYO_60", "process_id": "PROC_ETCH", "recipe_code": "RCP_ETCH_CRYO_N60", "param_name": "챔버 온도 및 C4F8 가스비", "target_value": "-60℃ / 1.25", "cost_impact": "+$8.50/wafer", "market_fab": "FAB_P4_NAND"},
                {"recipe_id": "RCP_ETCH_RF_POWER", "process_id": "PROC_ETCH", "recipe_code": "RCP_ETCH_RF_3200W", "param_name": "Source Dual RF 파워", "target_value": "3,200 W", "cost_impact": "+$1.80/wafer", "market_fab": "FAB_P4_NAND"},
                {"recipe_id": "RCP_ALD_HIGHK_280", "process_id": "PROC_DEPO", "recipe_code": "RCP_ALD_HZO_280C", "param_name": "High-K HZO 증착 온도", "target_value": "280 ℃", "cost_impact": "$0/wafer", "market_fab": "FAB_S5_FOUNDRY"},
                {"recipe_id": "RCP_CLEAN_SCCO2", "process_id": "PROC_CLEAN", "recipe_code": "RCP_CLEAN_SCCO2_DRY", "param_name": "초임계 CO2 건조 조건", "target_value": "73.8 bar / 31.1 ℃", "cost_impact": "+$3.10/wafer", "market_fab": "FAB_P3_DRAM"}
            ]),
            "dim_fab_line (생산 팹 라인 마스터)": pd.DataFrame([
                {"fab_id": "FAB_P3_DRAM", "fab_code": "P3-DRAM", "fab_name": "평택 P3 (1b nm DRAM 라인)", "site_location": "평택 캠퍼스", "cleanroom_grade": "Class 1", "capacity_wpm": "150k WPM"},
                {"fab_id": "FAB_P4_NAND", "fab_code": "P4-NAND", "fab_name": "평택 P4 (V9 300+단 NAND 라인)", "site_location": "평택 캠퍼스", "cleanroom_grade": "Class 1", "capacity_wpm": "120k WPM"},
                {"fab_id": "FAB_S5_FOUNDRY", "fab_code": "S5-GAA", "fab_name": "화성 S5 (SF3 3nm GAA 파운드리)", "site_location": "화성 캠퍼스", "cleanroom_grade": "Class 0.1", "capacity_wpm": "45k WPM"}
            ]),
            "dim_equipment_spec (설비/챔버 스펙 마스터)": pd.DataFrame([
                {"equipment_id": "EQ_ASML_NXE3800", "equipment_name": "ASML Twinscan NXE:3800F EUV", "vendor": "ASML", "unit_price_usd": "$220,000,000", "control_parameter": "13.5nm 파장 / 900W 광원 / 220 WPH"},
                {"equipment_id": "EQ_PELLICLE_CNT", "equipment_name": "Carbon Nanotube EUV 펠리클", "vendor": "삼성전자/협력사", "unit_price_usd": "$45,000", "control_parameter": "투과율 92.4% / 열변형 800W 한계"},
                {"equipment_id": "EQ_LAM_CRYO_ETCHER", "equipment_name": "Lam Research 극저온 유전체 식각기", "vendor": "Lam Research", "unit_price_usd": "$14,500,000", "control_parameter": "-70℃ ~ +60℃ 냉각 ESC / 60MHz Dual RF"},
                {"equipment_id": "EQ_TEL_INDY_ALD", "equipment_name": "TEL Certas LEAGEND High-K ALD", "vendor": "Tokyo Electron", "unit_price_usd": "$11,200,000", "control_parameter": "0.1Å 정밀 제어 / Step Coverage 99.8%"}
            ]),
            "rel_recipe_equipment (레시피-설비 매핑 테이블)": pd.DataFrame([
                {"recipe_id": "RCP_EUV_DOSE_45", "equipment_id": "EQ_ASML_NXE3800", "parameter_setting": "광원 900W + Scan Speed 연동", "weight_purchase": 0.1, "weight_info": 0.9},
                {"recipe_id": "RCP_EUV_DOSE_45", "equipment_id": "EQ_PELLICLE_CNT", "parameter_setting": "고내열 CNT 펠리클 장착", "weight_purchase": 0.1, "weight_info": 0.9},
                {"recipe_id": "RCP_ETCH_CRYO_60", "equipment_id": "EQ_LAM_CRYO_ETCHER", "parameter_setting": "ESC 칠러 -60℃ 고정", "weight_purchase": 0.1, "weight_info": 0.9},
                {"recipe_id": "RCP_ALD_HIGHK_280", "equipment_id": "EQ_TEL_INDY_ALD", "parameter_setting": "히터 블록 280℃ 균일화", "weight_purchase": 0.1, "weight_info": 0.9}
            ]),
            "rel_process_yield (공정-수율 영향도 매핑 테이블)": pd.DataFrame([
                {"process_id": "PROC_PHOTO", "impact_id": "YIELD_DEFECT_REDUCE", "correlation_score": 0.94, "defect_reduction": "-18.4%", "annual_savings": "연 180억원", "weight_info": 0.1, "weight_purchase": 0.9},
                {"process_id": "PROC_ETCH", "impact_id": "YIELD_HOLE_TILT_FIX", "correlation_score": 0.96, "defect_reduction": "틸트 불량 0%", "annual_savings": "연 260억원", "weight_info": 0.1, "weight_purchase": 0.9},
                {"process_id": "PROC_DEPO", "impact_id": "YIELD_LEAKAGE_SUPPRESS", "correlation_score": 0.91, "defect_reduction": "누설전류 -35%", "annual_savings": "수명 2배 증대", "weight_info": 0.1, "weight_purchase": 0.9},
                {"process_id": "PROC_CLEAN", "impact_id": "YIELD_PATTERN_COLLAPSE", "correlation_score": 0.98, "defect_reduction": "패턴 쓰러짐 0ppm", "annual_savings": "연 140억원", "weight_info": 0.1, "weight_purchase": 0.9}
            ])
        }


# =========================================================
# 2. 온톨로지 동적 가중치 규칙 및 서브그래프 탐색 알고리즘
# =========================================================
def get_edge_weight(relation: str, intent: str, domain_meta: dict) -> float:
    """
    온톨로지 공리 [Weight Rule]에 따라 의도(Intent)별 가중치를 산출합니다.
    """
    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]
    rel_filter = domain_meta["rel_filter"]

    if intent == "INFO_SEARCH":
        if relation == rel_mkt:
            return 0.1
        elif relation == rel_belongs:
            return 0.2
        elif relation == rel_filter:
            return 0.3
        elif relation == rel_spec:
            return 0.9
        else:
            return 0.5
    elif intent == "PURCHASE_INTENT":
        if relation == rel_spec:
            return 0.1
        elif relation == rel_belongs:
            return 0.2
        elif relation == rel_filter:
            return 0.3
        elif relation == rel_mkt:
            return 0.9
        else:
            return 0.5
    else:
        return 0.5


def explore_subgraph(nodes, edges, seed_node_id: str, intent: str, max_hop: int, weight_threshold: float, filter_val: str, domain_meta: dict):
    """
    시드 노드로부터 시작하여 가중치 임계값, Max Hop, 도메인 필터를 만족하는 활성 서브그래프를 탐색합니다.
    """
    G = nx.Graph()
    node_dict = {n["id"]: n for n in nodes}

    for n in nodes:
        G.add_node(n["id"], **n)

    all_evaluated_edges = []
    filter_type = domain_meta["filter_type"]
    child_type = domain_meta["child_type"]

    for edge in edges:
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = get_edge_weight(rel, intent, domain_meta)

        valid_filter = True
        if filter_val != "ALL":
            s_node = node_dict.get(s, {})
            t_node = node_dict.get(t, {})

            if s_node.get("type") == filter_type and s_node.get("attributes", {}).get("code") != filter_val:
                valid_filter = False
            if t_node.get("type") == filter_type and t_node.get("attributes", {}).get("code") != filter_val:
                valid_filter = False

            if s_node.get("type") == child_type and s_node.get("attributes", {}).get("market") != filter_val:
                valid_filter = False
            if t_node.get("type") == child_type and t_node.get("attributes", {}).get("market") != filter_val:
                valid_filter = False

        edge_info = {
            **edge,
            "dynamic_weight": w,
            "valid_filter": valid_filter
        }
        all_evaluated_edges.append(edge_info)

        if valid_filter:
            G.add_edge(s, t, key=rel, relation=rel, weight=w, desc=edge.get("desc", ""))

    active_nodes = {}
    active_edges = []

    if seed_node_id in G:
        active_nodes[seed_node_id] = {
            "hop": 0,
            "cost": 0.0,
            "relevance": 1.0
        }

        queue = [(seed_node_id, 0, 0.0)]
        visited_nodes = {seed_node_id: (0, 0.0)}

        while queue:
            curr_node, curr_hop, curr_cost = queue.pop(0)

            if curr_hop >= max_hop:
                continue

            for neighbor in G.neighbors(curr_node):
                edge_data = G.get_edge_data(curr_node, neighbor)
                w = edge_data.get("weight", 1.0)

                if w <= weight_threshold:
                    next_cost = curr_cost + w
                    next_hop = curr_hop + 1

                    if neighbor not in visited_nodes or next_cost < visited_nodes[neighbor][1]:
                        visited_nodes[neighbor] = (next_hop, next_cost)
                        relevance = round(1.0 / (1.0 + next_cost), 3)
                        active_nodes[neighbor] = {
                            "hop": next_hop,
                            "cost": round(next_cost, 2),
                            "relevance": relevance
                        }
                        queue.append((neighbor, next_hop, next_cost))

    for edge in all_evaluated_edges:
        s = edge["source"]
        t = edge["target"]
        w = edge["dynamic_weight"]
        valid_flt = edge["valid_filter"]

        is_active = (s in active_nodes) and (t in active_nodes) and (w <= weight_threshold) and valid_flt
        edge["is_active"] = is_active
        if is_active:
            active_edges.append(edge)

    return active_nodes, active_edges, all_evaluated_edges


# ==========================================
# 3. BigQuery GQL 및 LLM Context 생성기
# ==========================================
def generate_bigquery_gql(seed_node_id: str, intent: str, max_hop: int, weight_threshold: float, filter_val: str, node_dict: dict, domain_meta: dict) -> tuple:
    """
    도메인 및 의도에 따라 BigQuery GQL 표준 쿼리문 및 GRAPH_TABLE 멀티홉 서브그래프 쿼리를 생성합니다.
    (가격, 옵션가, 할인액 필드를 RETURN 절에 명시)
    """
    seed_node = node_dict.get(seed_node_id, {})
    seed_name = seed_node.get("name", "SeedEntity")
    seed_type = seed_node.get("type", domain_meta["parent_type"])
    dataset = domain_meta["bq_dataset"]
    domain_id = domain_meta["id"]

    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]
    child_type = domain_meta["child_type"]
    spec_type = domain_meta["spec_type"]
    mkt_type = domain_meta["mkt_type"]
    filter_type = domain_meta["filter_type"]

    filter_clause_gql = f"\n  AND (target.market = '{filter_val}' OR target.code = '{filter_val}')" if filter_val != "ALL" else ""
    filter_clause_gtable = f"\n        AND (target:{filter_type}.code = '{filter_val}' OR EXISTS {{ (target)-[:{domain_meta['rel_filter']}]->(:{filter_type} {{code: '{filter_val}'}}) }})" if filter_val != "ALL" else ""

    if domain_id == "automotive":
        if intent == "INFO_SEARCH":
            return_clause = """RETURN 
    p.name AS primary_entity,
    m.name AS marketing_title,
    m.discount AS promo_discount,
    m.desc AS benefit_details,
    e.weight AS relevance_cost"""
        else:
            return_clause = """RETURN 
    p.name AS primary_entity,
    c.name AS model_variant,
    c.base_price AS start_price,
    s.name AS spec_item,
    s.option_price AS add_on_price,
    e.weight AS option_priority_cost"""
    elif domain_id == "ecommerce":
        if intent == "INFO_SEARCH":
            return_clause = """RETURN 
    p.name AS primary_category,
    m.name AS promotion_title,
    m.discount_rate AS discount_pct,
    m.desc AS promo_details,
    e.weight AS relevance_cost"""
        else:
            return_clause = """RETURN 
    p.name AS primary_category,
    c.name AS product_sku,
    c.price AS retail_price,
    s.name AS spec_feature,
    s.option_price AS spec_grade,
    e.weight AS option_priority_cost"""
    elif domain_id == "telco":
        if intent == "INFO_SEARCH":
            return_clause = """RETURN 
    p.name AS primary_family,
    m.name AS benefit_title,
    m.benefit_val AS monthly_benefit_krw,
    m.desc AS benefit_details,
    e.weight AS relevance_cost"""
        else:
            return_clause = """RETURN 
    p.name AS primary_family,
    c.name AS plan_code,
    c.monthly_fee AS monthly_cost_krw,
    s.name AS spec_allowance,
    s.extra_fee AS extra_overage_cost,
    e.weight AS option_priority_cost"""
    else:
        if intent == "INFO_SEARCH":
            return_clause = """RETURN 
    p.name AS process_stage,
    m.name AS yield_impact_metric,
    m.annual_savings AS annual_cost_benefit,
    m.desc AS yield_impact_details,
    e.weight AS relevance_cost"""
        else:
            return_clause = """RETURN 
    p.name AS process_stage,
    c.name AS recipe_parameter,
    c.cost_impact AS recipe_cost_delta,
    s.name AS equipment_spec,
    s.eq_price AS equipment_capex,
    e.weight AS control_priority_cost"""

    if intent == "INFO_SEARCH":
        gql_standard = f"""-- =========================================================================
-- Google Cloud BigQuery GQL: [{domain_meta['name']}] 정보/영향도 탐색 의도 (INFO_SEARCH)
-- 목적: {mkt_type} 영향도 및 메트릭({rel_mkt}) 우선 추출
-- =========================================================================
GRAPH `{dataset}`
MATCH (p:{seed_type} {{name: '{seed_name}'}})-[e:{rel_mkt}]->(m:{mkt_type})
WHERE e.weight <= {weight_threshold:.2f}{filter_clause_gql}
{return_clause}
ORDER BY 
    relevance_cost ASC;"""
    else:
        gql_standard = f"""-- =========================================================================
-- Google Cloud BigQuery GQL: [{domain_meta['name']}] 레시피/설비 제어 의도 (PURCHASE_INTENT)
-- 목적: 세부 파라미터별 변경 비용 및 설비 스펙({rel_spec}) 정밀 추출
-- =========================================================================
GRAPH `{dataset}`
MATCH (p:{seed_type} {{name: '{seed_name}'}})<-[:{rel_belongs}]-(c:{child_type})-[e:{rel_spec}]->(s:{spec_type})
WHERE e.weight <= {weight_threshold:.2f}{filter_clause_gql}
{return_clause}
ORDER BY 
    option_priority_cost ASC;"""

    gql_graph_table = f"""-- =========================================================================
-- Google Cloud BigQuery GoogleSQL GQL (GRAPH_TABLE) Dynamic Subgraph Query
-- Domain: {domain_meta['name']} | Max Hop: {max_hop} | Weight Threshold: <= {weight_threshold:.2f}
-- =========================================================================
SELECT 
    path_hop,
    source_name,
    relationship_type,
    edge_weight,
    target_type,
    target_name,
    target_attributes,
    relevance_score
FROM GRAPH_TABLE(
    `{dataset}`,
    MATCH (start:{seed_type} {{id: '{seed_node_id}'}})
          -[e:{rel_belongs}|{domain_meta['rel_filter']}|{rel_mkt}|{rel_spec}*1..{max_hop}]-(target)
    WHERE e.weight <= {weight_threshold:.2f}{filter_clause_gtable}
    COLUMNS (
        LENGTH(e) AS path_hop,
        start.name AS source_name,
        LABEL(LAST(e)) AS relationship_type,
        LAST(e).weight AS edge_weight,
        LABEL(target) AS target_type,
        target.name AS target_name,
        target.attributes AS target_attributes,
        (1.0 / (1.0 + SUM(e.weight))) AS relevance_score
    )
)
ORDER BY 
    path_hop ASC, 
    relevance_score DESC, 
    edge_weight ASC;"""

    return gql_standard, gql_graph_table


def generate_bigquery_ddl(domain: str) -> str:
    """
    선택된 비즈니스 도메인에 대한 BigQuery CREATE OR REPLACE PROPERTY GRAPH DDL 스크립트를 생성합니다.
    """
    if "자동차" in domain or "automotive" in domain.lower():
        return """-- =========================================================================
-- 1. BigQuery Property Graph 정의: 자동차 도메인 (Automotive)
-- 데이터셋: `gcp-project-auto-kg.vehicle_ontology.car_knowledge_graph`
-- =========================================================================
CREATE OR REPLACE PROPERTY GRAPH `gcp-project-auto-kg.vehicle_ontology.car_knowledge_graph`
  NODE TABLES (
    dim_family_car 
      KEY (family_id) 
      LABEL FamilyCar 
      PROPERTIES (family_name, brand, segment, seats),
    dim_model_code 
      KEY (model_id) 
      LABEL ModelCode 
      PROPERTIES (model_code, powertrain, base_price, base_price_formatted, market, launch_year),
    dim_region_market 
      KEY (region_id) 
      LABEL Region 
      PROPERTIES (region_code, region_name, currency, ev_subsidy),
    dim_spec_item 
      KEY (spec_id) 
      LABEL SpecItem 
      PROPERTIES (spec_name, category, option_price, spec_details),
    dim_marketing_info 
      KEY (mkt_id) 
      LABEL MarketingInfo 
      PROPERTIES (ksp_title, discount_benefit, content)
  )
  EDGE TABLES (
    dim_model_code AS rel_model_family 
      KEY (model_id, family_id)
      SOURCE KEY (model_id) REFERENCES dim_model_code(model_id)
      DESTINATION KEY (family_id) REFERENCES dim_family_car(family_id)
      LABEL BELONGS_TO,
    rel_model_region 
      KEY (model_id, region_id)
      SOURCE KEY (model_id) REFERENCES dim_model_code(model_id)
      DESTINATION KEY (region_id) REFERENCES dim_region_market(region_id)
      LABEL AVAILABLE_IN 
      PROPERTIES (weight_purchase, weight_info, is_primary_market, base_price),
    rel_model_spec 
      KEY (model_id, spec_id)
      SOURCE KEY (model_id) REFERENCES dim_model_code(model_id)
      DESTINATION KEY (spec_id) REFERENCES dim_spec_item(spec_id)
      LABEL APPLIES_SPEC 
      PROPERTIES (weight_purchase, weight_info, option_price),
    rel_family_marketing 
      KEY (family_id, mkt_id)
      SOURCE KEY (family_id) REFERENCES dim_family_car(family_id)
      DESTINATION KEY (mkt_id) REFERENCES dim_marketing_info(mkt_id)
      LABEL HAS_KSP 
      PROPERTIES (weight_info, weight_purchase, discount_benefit)
  );"""

    elif "이커머스" in domain or "ecommerce" in domain.lower():
        return """-- =========================================================================
-- 2. BigQuery Property Graph 정의: 이커머스 도메인 (E-Commerce)
-- 데이터셋: `gcp-project-ecommerce.catalog_ontology.product_semantic_graph`
-- =========================================================================
CREATE OR REPLACE PROPERTY GRAPH `gcp-project-ecommerce.catalog_ontology.product_semantic_graph`
  NODE TABLES (
    dim_brand_category 
      KEY (category_id) 
      LABEL BrandCategory 
      PROPERTIES (brand_name, category_name, season, target_sports),
    dim_product_sku 
      KEY (sku_id) 
      LABEL ProductSKU 
      PROPERTIES (sku_code, product_name, price, price_formatted, weight_g, target_segment),
    dim_target_segment 
      KEY (segment_id) 
      LABEL TargetSegment 
      PROPERTIES (segment_code, segment_name, experience_level),
    dim_product_spec 
      KEY (spec_id) 
      LABEL ProductSpec 
      PROPERTIES (spec_name, feature_category, spec_value, option_price),
    dim_promo_event 
      KEY (promo_id) 
      LABEL PromoEvent 
      PROPERTIES (promo_title, discount_rate, discount_val, period)
  )
  EDGE TABLES (
    dim_product_sku AS rel_sku_category 
      KEY (sku_id, category_id)
      SOURCE KEY (sku_id) REFERENCES dim_product_sku(sku_id)
      DESTINATION KEY (category_id) REFERENCES dim_brand_category(category_id)
      LABEL BELONGS_TO,
    dim_product_sku AS rel_sku_segment 
      KEY (sku_id, target_segment)
      SOURCE KEY (sku_id) REFERENCES dim_product_sku(sku_id)
      DESTINATION KEY (target_segment) REFERENCES dim_target_segment(segment_id)
      LABEL TARGETS,
    rel_sku_spec 
      KEY (sku_id, spec_id)
      SOURCE KEY (sku_id) REFERENCES dim_product_sku(sku_id)
      DESTINATION KEY (spec_id) REFERENCES dim_product_spec(spec_id)
      LABEL APPLIES_SPEC 
      PROPERTIES (weight_purchase, weight_info, option_price),
    rel_category_promo 
      KEY (category_id, promo_id)
      SOURCE KEY (category_id) REFERENCES dim_brand_category(category_id)
      DESTINATION KEY (promo_id) REFERENCES dim_promo_event(promo_id)
      LABEL HAS_PROMO 
      PROPERTIES (weight_info, weight_purchase, discount_rate)
  );"""

    elif "모바일" in domain or "요금제" in domain or "telco" in domain.lower():
        return """-- =========================================================================
-- 3. BigQuery Property Graph 정의: 모바일 요금제 도메인 (Telco)
-- 데이터셋: `gcp-project-telco.plan_ontology.telco_plan_semantic_graph`
-- =========================================================================
CREATE OR REPLACE PROPERTY GRAPH `gcp-project-telco.plan_ontology.telco_plan_semantic_graph`
  NODE TABLES (
    dim_plan_family 
      KEY (family_id) 
      LABEL PlanFamily 
      PROPERTIES (family_name, network_type, target_tier, voice_sms),
    dim_plan_code 
      KEY (plan_id) 
      LABEL PlanCode 
      PROPERTIES (plan_code, plan_name, monthly_fee, monthly_fee_formatted, target_user),
    dim_target_user 
      KEY (user_id) 
      LABEL TargetUser 
      PROPERTIES (user_code, user_group_name, age_criteria),
    dim_plan_spec 
      KEY (spec_id) 
      LABEL PlanSpec 
      PROPERTIES (spec_name, data_allowance, qos_speed, extra_fee, tethering_limit),
    dim_marketing_benefit 
      KEY (benefit_id) 
      LABEL MarketingBenefit 
      PROPERTIES (benefit_name, monthly_value, ott_partner)
  )
  EDGE TABLES (
    dim_plan_code AS rel_plan_family 
      KEY (plan_id, family_id)
      SOURCE KEY (plan_id) REFERENCES dim_plan_code(plan_id)
      DESTINATION KEY (family_id) REFERENCES dim_plan_family(family_id)
      LABEL BELONGS_TO,
    dim_plan_code AS rel_plan_target 
      KEY (plan_id, target_user)
      SOURCE KEY (plan_id) REFERENCES dim_plan_code(plan_id)
      DESTINATION KEY (target_user) REFERENCES dim_target_user(user_id)
      LABEL TARGETS,
    rel_plan_spec 
      KEY (plan_id, spec_id)
      SOURCE KEY (plan_id) REFERENCES dim_plan_code(plan_id)
      DESTINATION KEY (spec_id) REFERENCES dim_plan_spec(spec_id)
      LABEL APPLIES_PLAN_SPEC 
      PROPERTIES (weight_purchase, weight_info, extra_fee),
    rel_plan_benefit 
      KEY (plan_id, benefit_id)
      SOURCE KEY (plan_id) REFERENCES dim_plan_code(plan_id)
      DESTINATION KEY (benefit_id) REFERENCES dim_marketing_benefit(benefit_id)
      LABEL HAS_BENEFIT 
      PROPERTIES (weight_info, weight_purchase, monthly_value)
  );"""

    else:
        return """-- =========================================================================
-- 4. BigQuery Property Graph 정의: 반도체 8대 공정 및 레시피 (Semiconductor)
-- 데이터셋: `gcp-project-semicon.fab_ontology.semiconductor_process_graph`
-- =========================================================================
CREATE OR REPLACE PROPERTY GRAPH `gcp-project-semicon.fab_ontology.semiconductor_process_graph`
  NODE TABLES (
    dim_process_stage 
      KEY (process_id) 
      LABEL ProcessStage 
      PROPERTIES (stage_no, process_name, tech_node, key_metric),
    dim_recipe_param 
      KEY (recipe_id) 
      LABEL RecipeParam 
      PROPERTIES (recipe_code, param_name, target_value, cost_impact, market_fab),
    dim_fab_line 
      KEY (fab_id) 
      LABEL FabLine 
      PROPERTIES (fab_code, fab_name, site_location, cleanroom_grade),
    dim_equipment_spec 
      KEY (equipment_id) 
      LABEL EquipmentSpec 
      PROPERTIES (equipment_name, vendor, unit_price_usd, control_parameter),
    dim_yield_impact 
      KEY (impact_id) 
      LABEL YieldImpact 
      PROPERTIES (metric_title, defect_reduction, annual_savings, yield_gain)
  )
  EDGE TABLES (
    dim_recipe_param AS rel_recipe_process 
      KEY (recipe_id, process_id)
      SOURCE KEY (recipe_id) REFERENCES dim_recipe_param(recipe_id)
      DESTINATION KEY (process_id) REFERENCES dim_process_stage(process_id)
      LABEL BELONGS_TO,
    dim_recipe_param AS rel_recipe_fab 
      KEY (recipe_id, market_fab)
      SOURCE KEY (recipe_id) REFERENCES dim_recipe_param(recipe_id)
      DESTINATION KEY (market_fab) REFERENCES dim_fab_line(fab_id)
      LABEL RUNS_ON,
    rel_recipe_equipment 
      KEY (recipe_id, equipment_id)
      SOURCE KEY (recipe_id) REFERENCES dim_recipe_param(recipe_id)
      DESTINATION KEY (equipment_id) REFERENCES dim_equipment_spec(equipment_id)
      LABEL CONTROLS_EQUIPMENT 
      PROPERTIES (weight_purchase, weight_info, parameter_setting),
    rel_process_yield 
      KEY (process_id, impact_id)
      SOURCE KEY (process_id) REFERENCES dim_process_stage(process_id)
      DESTINATION KEY (impact_id) REFERENCES dim_yield_impact(impact_id)
      LABEL AFFECTS_YIELD 
      PROPERTIES (weight_info, weight_purchase, correlation_score)
  );"""


def build_llm_context_and_response(intent: str, seed_node_id: str, active_nodes: dict, active_edges: list, node_dict: dict, user_query: str, domain_meta: dict):
    """
    활성화된 온톨로지 서브그래프를 LLM Context로 구조화하고 도메인별 Mock 답변을 생성합니다.
    """
    seed_node = node_dict.get(seed_node_id, {})
    domain_id = domain_meta["id"]

    extracted_specs = []
    extracted_mkt = []
    extracted_children = []

    spec_type = domain_meta["spec_type"]
    mkt_type = domain_meta["mkt_type"]
    child_type = domain_meta["child_type"]

    for nid, meta in active_nodes.items():
        if nid == seed_node_id:
            continue
        n = node_dict.get(nid, {})
        ntype = n.get("type")
        nname = n.get("name")
        ndesc = n.get("desc")
        nattr = n.get("attributes", {})

        if ntype == spec_type:
            extracted_specs.append(f"• **{nname}**: {ndesc} ({json.dumps(nattr, ensure_ascii=False)})")
        elif ntype == mkt_type:
            extracted_mkt.append(f"• **{nname}**: {ndesc}")
        elif ntype == child_type:
            extracted_children.append(f"• **{nname}** ({json.dumps(nattr, ensure_ascii=False)})")

    context_payload = {
        "domain": domain_meta["name"],
        "user_query": user_query,
        "inferred_intent": intent,
        "seed_entity": {
            "id": seed_node.get("id"),
            "name": seed_node.get("name"),
            "type": seed_node.get("type"),
            "desc": seed_node.get("desc")
        },
        "ontology_filtered_knowledge": {
            f"active_{child_type}": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == child_type],
            f"active_{mkt_type}": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == mkt_type],
            f"active_{spec_type}": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == spec_type],
            "total_active_entities": len(active_nodes),
            "total_active_relations": len(active_edges)
        }
    }

    # 도메인별 LLM 응답 시뮬레이션 (가격 및 비용 정보 포함)
    if domain_id == "automotive":
        if intent == "INFO_SEARCH":
            llm_text = f"""### 📢 [소렌토/싼타페 마케팅 & 신차 프로모션 견적 안내]
고객님께서 문의하신 최신 프로모션 및 할인 혜택 하이라이트입니다:
1. **2025 신형 출시 & 사전계약 혜택**: 연 2.9% 저금리 할부 및 **50만원 바우처 지원** (사전예약 특전).
2. **스타맵 라이팅 & 스타일 패키지**: 첨단 수직형 DRL 스타일 패키지 선택 시 **30만원 할인 지원**.
3. **친환경 하이브리드 세제 혜택**: 복합 15.7km/L 연비 및 **개별소비세/취득세 최대 143만원 감면**."""
        else:
            llm_text = f"""### 🛒 [소렌토/싼타페 트림별 출고가 및 추천 옵션 견적]
구매 의도에 맞춰 지식 그래프 온톨로지 기반으로 필터링된 출고가 및 패키지 견적입니다:
1. **추천 모델 및 기본 출고가**:
   - **MQ4 HEV 하이브리드 [3,780만원~]** / **MX5 HEV 하이브리드 [3,880만원~]**
2. **필수 추천 옵션 패키지 및 추가 비용**:
   - **1.6T HEV 전용 엔진 (+기본포함)**
   - **드라이브 와이즈 ADAS (+120만원)**: HDA2 고속도로 주행 보조 패키지
   - **전자식 AWD 4륜구동 (+200만원)**: 터레인 모드 연동 4WD
   - **10인치 헤드업 디스플레이 (+70만원)** / **QHD 빌트인 캠 2 (+45만원)**"""

    elif domain_id == "ecommerce":
        if intent == "INFO_SEARCH":
            llm_text = f"""### 🛍️ [이커머스 러닝/캠핑 기획전 및 할인 쿠폰 안내]
문의하신 카테고리의 최신 할인 쿠폰 및 사은품 혜택 정보입니다:
1. **봄맞이 시즌오프 기획전 (20% 할인 쿠폰)**: 전 상품 20% 즉시 할인 (최대 7만원 할인 한도).
2. **신규 런칭 기념 프로모션**: 알파플라이 3 론칭 기념 **드라이핏 레이싱 삭스 증정 + 1만원 추가 할인**.
3. **아웃도어 페스타 증정 행사**: 패밀리 텐트/쉘터 구매 고객 대상 **12만원 상당 방수 그라운드시트 무료 증정**."""
        else:
            llm_text = f"""### 👟 [러닝화 & 캠핑 장비 정가 및 스펙 가치 비교]
고객님의 퍼포먼스 및 용도에 맞춘 온톨로지 기반 정가 및 사양 분석입니다:
1. **에어줌 알파플라이 3 [359,000원]**: **ZoomX 고반발 폼 (+핵심 사양)** + **풀렝스 카본 플라이플레이트 (+프리미엄)** 탑재 (218g).
2. **나이키 페가수스 41 [159,000원]**: **ReactX 쿠셔닝 폼 (+친환경 에코)** 탑재로 일상 러닝 데일리 트레이너 추천.
3. **어메니티 돔 4인용 텐트 [498,000원]**: **내수압 3,000mm 립스탑 (+고내수압 원단)** + **두랄루민 7001 폴대 (+초경량)** 기본 적용."""

    elif domain_id == "telco":
        if intent == "INFO_SEARCH":
            llm_text = f"""### 📱 [모바일 5G 요금제 부가 혜택 & 멤버십 가치 환산]
고객님께 적합한 5G 요금제 무료 혜택 및 연간 환산 가치입니다:
1. **넷플릭스 + 디즈니+ 무료팩**: **5G 프리미어 슈퍼 [월 115,000원]** 가입 시 **월 24,000원 상당 OTT 구독료 100% 무료 지원**.
2. **VVIP 영화 무료 멤버십**: CGV/메가박스 영화 연 12회 무료 예매권 (**연 180,000원 상당 혜택**).
3. **U+ 투게더 결합할인**: 가족 결합 시 **회선당 최대 20,000원 월정액 추가 감면**."""
        else:
            llm_text = f"""### ⚡ [5G 요금제 월정액 & 초과 과금 상세 스펙 분석]
실구매 및 요금제 변경을 위한 상세 월 요금 및 데이터 스펙 분석입니다:
1. **5G 프리미어 슈퍼 [월 115,000원]**: **데이터 완전무제한 (+테더링 50GB 공유, 추가과금 0원)** + **스마트기기 2회선 (+월 22,000원 무료)**.
2. **너겟 5G 청년 무제한 [월 59,000원]**: 만 34세 이하 무약정 온라인 요금제, 기본 12GB 소진 후에도 **5Mbps QoS (추가요금 無, FHD 유튜브 가능)**.
3. **5G 시니어 49 [월 49,000원]**: 만 65세 이상 어르신 전용, 기본 15GB + **보이스피싱 안심 보험 (최대 300만원 무상 보상)** 무료."""

    else:
        # 반도체 8대 공정 (Semiconductor)
        if intent == "INFO_SEARCH":
            llm_text = f"""### 🔬 [삼성전자DS 8대 공정 레시피 변경에 따른 수율 및 품질 영향도 분석]
선택된 레시피 변경 파라미터에 대한 지식 그래프 온톨로지 기반 영향도 시뮬레이션 결과입니다:
1. **EUV 포토 공정 (Dose 45mJ/cm² 상향)**:
   - **품질 영향**: 라인 에지 러프니스(LER) 및 마이크로 브릿지 결함률 **18.4% 감소**, 수율 **+1.8%p 개선**.
   - **비용 영향**: 연간 웨이퍼 폐기 비용 **180억원 절감** (웨이퍼당 추가 공정비 +$4.20 상쇄).
2. **HARC 고선택비 플라즈마 식각 (극저온 -60℃ / C4F8:CF4=1.25)**:
   - **품질 영향**: 300단 V-NAND 채널 홀 기울어짐/휨 불량 차단으로 **수율 +3.2%p 향상**.
   - **경제적 가치**: 연간 수율 개선 효과 **260억원 창출**.
3. **초임계 CO2 건조 세정**: 1b nm D램 커패시터 패턴 붕괴 결함률 **Zero 달성** (수율 +2.5%p 개선)."""
        else:
            llm_text = f"""### ⚙️ [삼성전자DS 8대 공정 설비 챔버 스펙 및 레시피 제어 조건 분석]
레시피 변경을 적용하기 위한 핵심 반도체 제조 장비 사양 및 챔버 제어 스펙입니다:
1. **ASML Twinscan NXE:3800F ($220M / 220 WPH)**:
   - **제어 스펙**: 13.5nm 파장 High-Dose 극자외선 노광 시스템, 시간당 220매 고생산성 처리.
   - **펠리클 사양**: 탄소나노튜브(CNT) 펠리클 투과율 92.4% 유지 및 800W 고출력 광원 열변형 한계 충족.
2. **Lam Research 극저온 유전체 식각기 ($14.5M)**:
   - **챔버 스펙**: -70℃~+60℃ 정전척(ESC) 냉각 칠러 제어 및 60MHz/2MHz Dual RF 펄스 동기화.
3. **TEL Certas LEAGEND High-K ALD ($11.2M)**:
   - **박막 스펙**: 3nm GAA MBCFET 다층 채널 280℃ 균일 증착 (0.1Å 정밀 제어, Step Coverage 99.8%)."""

    return context_payload, llm_text, extracted_specs, extracted_mkt, extracted_children


# =========================================================
# 4. 공통 텍스트 툴팁 생성 헬퍼
# =========================================================
def create_node_plain_tooltip(node: dict, is_active: bool, is_seed: bool, active_meta: dict) -> str:
    """
    유니코드 심볼과 줄바꿈(\\n)을 활용한 표준 노드 툴팁 텍스트를 생성합니다.
    """
    nid = node["id"]
    ntype = node["type"]
    nname = node["name"]
    ndesc = node["desc"]
    nattr = node.get("attributes", {})

    status_str = "★ 시작 노드 (Seed Node)" if is_seed else ("🟢 활성 노드 (탐색 경로 포함)" if is_active else "⚪ 비활성 노드 (미탐색)")

    lines = [
        f"📌 {nname}",
        "────────────────────────",
        f"• 분류 (Type): {ntype}",
        f"• 노드 ID: {nid}",
        f"• 상태: {status_str}",
        f"• 설명: {ndesc}"
    ]

    if nattr:
        lines.append("────────────────────────")
        lines.append("🏷️ 상세 속성 (Attributes):")
        for k, v in nattr.items():
            lines.append(f"  · {k}: {v}")

    if is_active and active_meta:
        hop = active_meta.get("hop", 0)
        cost = active_meta.get("cost", 0.0)
        relevance = active_meta.get("relevance", 1.0)
        lines.append("────────────────────────")
        lines.append(f"🔍 탐색 정보: Hop {hop} | 비용(Cost) {cost:.2f} | 연관도(Relevance) {relevance:.3f}")

    return "\n".join(lines)


def create_edge_plain_tooltip(edge: dict, is_active: bool, s_name: str, t_name: str) -> str:
    """
    유니코드 심볼과 줄바꿈(\\n)을 활용한 표준 엣지 툴팁 텍스트를 생성합니다.
    """
    rel = edge["relation"]
    w = edge["dynamic_weight"]
    desc = edge.get("desc", "")

    status_str = "🟢 활성 탐색 경로 (Active Traversed)" if is_active else "⚪ 비활성 경로 (Pruned / Inactive)"
    priority_label = "🔥 최우선 탐색" if w <= 0.2 else ("⚡ 보조 경로" if w <= 0.5 else "⛔ 탐색 제외/후순위")

    lines = [
        f"⚡ 관계: {rel} ({w:.1f})",
        "────────────────────────",
        f"• 경로: {s_name} ➔ {t_name}",
        f"• 상태: {status_str}",
        f"• 가중치 비용: {w:.1f} ({priority_label})"
    ]
    if desc:
        lines.append(f"• 설명: {desc}")

    return "\n".join(lines)


# =========================================================
# 5. 그래프 렌더러 1: PyVis (Vis.js 물리 시뮬레이션)
# =========================================================
def render_pyvis_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict, domain_meta: dict) -> str:
    """
    선택된 IDE 테마 팔레트가 완벽하게 적용된 PyVis 물리 엔진(ForceAtlas2) HTML을 생성합니다.
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    node_colors = get_theme_node_color_map(theme, domain_meta)

    net = Network(height="680px", width="100%", bgcolor=graph_bg, font_color=text_color, directed=True, cdn_resources="remote")

    parent_type = domain_meta["parent_type"]
    child_type = domain_meta["child_type"]
    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]

    for node in nodes:
        nid = node["id"]
        ntype = node["type"]
        nname = node["name"]
        is_active = nid in active_nodes
        is_seed = (nid == seed_node_id)

        node_theme_color = node_colors.get(ntype, "#64748B")
        active_meta = active_nodes.get(nid, {})
        plain_node_tooltip = create_node_plain_tooltip(node, is_active, is_seed, active_meta)

        if is_active:
            hop = active_nodes[nid]["hop"]
            relevance = active_nodes[nid]["relevance"]

            if is_seed:
                size = 40
                b_width = 5
                b_color = "#F59E0B"
                b_bg = node_theme_color
                label_text = f"★ {nname}"
                font_size = 15
            else:
                size = 28 if ntype in [parent_type, child_type] else 22
                b_width = 3
                b_color = border_color
                b_bg = node_theme_color
                label_text = f"{nname}\n(h={hop}, r={relevance})"
                font_size = 12

            font_color = "#FFFFFF" if is_dark else "#0F172A"
            font_dict = {
                "size": font_size,
                "color": font_color,
                "face": "Pretendard, -apple-system, sans-serif",
                "strokeWidth": 3,
                "strokeColor": graph_bg
            }
            opacity = 1.0
        else:
            size = 15
            b_width = 1
            b_color = border_color
            b_bg = card_bg
            label_text = nname
            font_size = 10
            font_dict = {
                "size": 10,
                "color": "#94A3B8" if is_dark else "#64748B",
                "face": "Pretendard, -apple-system, sans-serif",
                "strokeWidth": 2,
                "strokeColor": graph_bg
            }
            opacity = 0.25

        net.add_node(
            nid,
            label=label_text,
            title=plain_node_tooltip,
            color={
                "background": b_bg,
                "border": b_color,
                "highlight": {"background": "#F59E0B", "border": "#FFFFFF"}
            },
            size=size,
            borderWidth=b_width,
            font=font_dict,
            opacity=opacity,
            shape="dot"
        )

    for edge in all_evaluated_edges:
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = edge["dynamic_weight"]
        is_active = edge.get("is_active", False)

        s_name = node_dict.get(s, {}).get("name", s)
        t_name = node_dict.get(t, {}).get("name", t)
        plain_edge_tooltip = create_edge_plain_tooltip(edge, is_active, s_name, t_name)

        if is_active:
            if rel == rel_mkt:
                edge_color = node_colors.get(domain_meta["mkt_type"], "#C084FC")
            elif rel == rel_spec:
                edge_color = node_colors.get(domain_meta["spec_type"], "#4ADE80")
            elif rel == rel_belongs:
                edge_color = node_colors.get(domain_meta["parent_type"], "#60A5FA")
            else:
                edge_color = node_colors.get(domain_meta["filter_type"], "#22D3EE")

            edge_font_color = "#F8FAFC" if is_dark else "#0F172A"
            net.add_edge(
                s, t,
                label=f"{rel} ({w:.1f})",
                title=plain_edge_tooltip,
                color=edge_color,
                width=2.8,
                arrows="to",
                font={"size": 11, "color": edge_font_color, "align": "middle", "strokeWidth": 3, "strokeColor": graph_bg},
                smooth={"type": "curvedCW", "roundness": 0.15}
            )
        else:
            net.add_edge(
                s, t,
                title=plain_edge_tooltip,
                color=f"{border_color}70",
                width=1.0,
                dashes=True,
                arrows="to",
                smooth={"type": "curvedCW", "roundness": 0.1}
            )

    physics_options = {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -140,
                "centralGravity": 0.003,
                "springLength": 250,
                "springConstant": 0.045,
                "damping": 0.88,
                "avoidOverlap": 0.85
            },
            "solver": "forceAtlas2Based",
            "stabilization": {
                "enabled": True,
                "iterations": 220,
                "updateInterval": 25
            }
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 60,
            "navigationButtons": True,
            "zoomView": True,
            "dragView": True,
            "dragNodes": True,
            "keyboard": True
        }
    }
    net.set_options(json.dumps(physics_options))

    html = net.generate_html()

    custom_tooltip_css = f"""
    <style>
    div.vis-tooltip {{
        position: absolute;
        background: {card_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        font-size: 12.5px !important;
        line-height: 1.6 !important;
        box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.4)' if is_dark else 'rgba(0, 0, 0, 0.12)'} !important;
        pointer-events: none !important;
        z-index: 99999 !important;
        max-width: 320px !important;
        white-space: pre-line !important;
        word-break: keep-all !important;
    }}
    </style>
    """
    injected_html = html.replace("</head>", f"{custom_tooltip_css}\n</head>")
    return injected_html


# =========================================================
# 6. 그래프 렌더러 2: Cytoscape.js (구조적 엔지니어링 레이아웃)
# =========================================================
def render_cytoscape_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict, domain_meta: dict) -> str:
    """
    선택된 IDE 테마 팔레트가 완벽하게 적용된 Cytoscape.js COSE 레이아웃 그래프 HTML을 생성합니다.
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    node_colors = get_theme_node_color_map(theme, domain_meta)

    parent_type = domain_meta["parent_type"]
    child_type = domain_meta["child_type"]
    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]

    elements = []

    for node in nodes:
        nid = node["id"]
        ntype = node["type"]
        nname = node["name"]
        is_active = nid in active_nodes
        is_seed = (nid == seed_node_id)
        active_meta = active_nodes.get(nid, {})

        node_tooltip = create_node_plain_tooltip(node, is_active, is_seed, active_meta)
        node_color = node_colors.get(ntype, "#64748B")

        elements.append({
            "data": {
                "id": nid,
                "label": f"★ {nname}" if is_seed else nname,
                "type": ntype,
                "is_active": is_active,
                "is_seed": is_seed,
                "bg_color": node_color if is_active else card_bg,
                "border_color": "#F59E0B" if is_seed else (node_color if is_active else border_color),
                "border_width": 4 if is_seed else (2 if is_active else 1),
                "size": 56 if is_seed else (44 if ntype in [parent_type, child_type] and is_active else (36 if is_active else 24)),
                "opacity": 1.0 if is_active else 0.3,
                "tooltip": node_tooltip
            }
        })

    for idx, edge in enumerate(all_evaluated_edges):
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = edge["dynamic_weight"]
        is_active = edge.get("is_active", False)

        s_name = node_dict.get(s, {}).get("name", s)
        t_name = node_dict.get(t, {}).get("name", t)
        edge_tooltip = create_edge_plain_tooltip(edge, is_active, s_name, t_name)

        if rel == rel_mkt:
            edge_color = node_colors.get(domain_meta["mkt_type"], "#C084FC")
        elif rel == rel_spec:
            edge_color = node_colors.get(domain_meta["spec_type"], "#4ADE80")
        elif rel == rel_belongs:
            edge_color = node_colors.get(domain_meta["parent_type"], "#60A5FA")
        else:
            edge_color = node_colors.get(domain_meta["filter_type"], "#22D3EE")

        elements.append({
            "data": {
                "id": f"e_{idx}_{s}_{t}",
                "source": s,
                "target": t,
                "label": f"{rel} ({w:.1f})" if is_active else "",
                "relation": rel,
                "weight": w,
                "is_active": is_active,
                "edge_color": edge_color if is_active else border_color,
                "width": 2.8 if is_active else 1.0,
                "opacity": 1.0 if is_active else 0.22,
                "line_style": "solid" if is_active else "dashed",
                "tooltip": edge_tooltip
            }
        })

    elements_json = json.dumps(elements, ensure_ascii=False)
    node_label_color = "#FFFFFF" if is_dark else "#0F172A"
    edge_label_color = "#F8FAFC" if is_dark else "#0F172A"

    cytoscape_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: {graph_bg};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #cy {{
            width: 100%;
            height: 680px;
            position: relative;
        }}
        #cy-tooltip {{
            position: absolute;
            display: none;
            background: {card_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 12.5px;
            line-height: 1.6;
            box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.4)' if is_dark else 'rgba(0, 0, 0, 0.12)'};
            pointer-events: none;
            z-index: 99999;
            max-width: 320px;
            white-space: pre-line;
            word-break: keep-all;
        }}
    </style>
</head>
<body>
    <div id="cy"></div>
    <div id="cy-tooltip"></div>

    <script>
        var cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: {elements_json},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'label': 'data(label)',
                        'color': '{node_label_color}',
                        'font-size': '11px',
                        'font-weight': '600',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-wrap': 'wrap',
                        'text-max-width': '85px',
                        'background-color': 'data(bg_color)',
                        'border-color': 'data(border_color)',
                        'border-width': 'data(border_width)',
                        'width': 'data(size)',
                        'height': 'data(size)',
                        'opacity': 'data(opacity)',
                        'text-outline-color': '{graph_bg}',
                        'text-outline-width': '3px'
                    }}
                }},
                {{
                    selector: 'node[?is_seed]',
                    style: {{
                        'font-size': '13px',
                        'font-weight': 'bold',
                        'text-outline-width': '3.5px'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'curve-style': 'bezier',
                        'line-color': 'data(edge_color)',
                        'width': 'data(width)',
                        'opacity': 'data(opacity)',
                        'line-style': 'data(line_style)',
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': 'data(edge_color)',
                        'arrow-scale': 1.1,
                        'label': 'data(label)',
                        'font-size': '10px',
                        'font-weight': 'bold',
                        'color': '{edge_label_color}',
                        'text-background-opacity': 0.95,
                        'text-background-color': '{graph_bg}',
                        'text-background-padding': '3px',
                        'text-background-shape': 'roundrectangle',
                        'text-rotation': 'autorotate'
                    }}
                }}
            ],
            layout: {{
                name: 'cose',
                animate: true,
                animationDuration: 700,
                nodeRepulsion: function(node) {{ return 750000; }},
                idealEdgeLength: function(edge) {{ return 130; }},
                edgeElasticity: function(edge) {{ return 100; }},
                gravity: 0.15,
                numIter: 1000,
                fit: true,
                padding: 40
            }}
        }});

        var tooltip = document.getElementById('cy-tooltip');

        cy.on('mouseover', 'node, edge', function(evt) {{
            var ele = evt.target;
            var text = ele.data('tooltip');
            if (text) {{
                tooltip.innerHTML = text;
                tooltip.style.display = 'block';
            }}
        }});

        cy.on('mousemove', function(evt) {{
            tooltip.style.left = (evt.renderedPosition.x + 15) + 'px';
            tooltip.style.top = (evt.renderedPosition.y + 15) + 'px';
        }});

        cy.on('mouseout', 'node, edge', function(evt) {{
            tooltip.style.display = 'none';
        }});
    </script>
</body>
</html>"""
    return cytoscape_html


# =========================================================
# 7. 그래프 렌더러 3: 3D Force Graph (WebGL 3차원 우주 궤도 뷰)
# =========================================================
def render_3d_force_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict, domain_meta: dict) -> str:
    """
    선택된 IDE 테마 팔레트와 순수 HTML5 Canvas 텍스처 스프라이트 레이블이 상시 표시되는 3D Force-Directed WebGL 우주 궤도 뷰 HTML을 생성합니다.
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    accent_color = theme.get("accent", "#38BDF8")
    node_colors = get_theme_node_color_map(theme, domain_meta)

    parent_type = domain_meta["parent_type"]
    child_type = domain_meta["child_type"]
    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]

    g_nodes = []
    for node in nodes:
        nid = node["id"]
        ntype = node["type"]
        nname = node["name"]
        is_active = nid in active_nodes
        is_seed = (nid == seed_node_id)
        active_meta = active_nodes.get(nid, {})

        node_tooltip = create_node_plain_tooltip(node, is_active, is_seed, active_meta)
        node_color = node_colors.get(ntype, "#64748B")
        if is_seed:
            node_color = "#FFD700" if is_dark else "#E11D48"
        elif not is_active:
            node_color = "#475569" if is_dark else "#94A3B8"

        g_nodes.append({
            "id": str(nid),
            "name": f"[{ntype}] {nname}" if not is_seed else f"★ [{ntype}] {nname} (Seed)",
            "short_label": nname,
            "type": ntype,
            "val": 16 if is_seed else (10 if is_active else 5),
            "color": node_color,
            "is_active": is_active,
            "is_seed": is_seed,
            "text_color": ("#FFFFFF" if is_dark else "#0F172A") if is_active else ("#B0BEC5" if is_dark else "#64748B"),
            "tooltip": node_tooltip
        })

    g_links = []
    for idx, edge in enumerate(all_evaluated_edges):
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = edge["dynamic_weight"]
        is_edge_active = edge.get("is_active", False)

        s_name = node_dict.get(s, {}).get("name", s)
        t_name = node_dict.get(t, {}).get("name", t)
        edge_tooltip = create_edge_plain_tooltip(edge, is_edge_active, s_name, t_name)

        if rel == rel_mkt:
            edge_color = node_colors.get(domain_meta["mkt_type"], "#C084FC")
        elif rel == rel_spec:
            edge_color = node_colors.get(domain_meta["spec_type"], "#4ADE80")
        elif rel == rel_belongs:
            edge_color = node_colors.get(domain_meta["parent_type"], "#60A5FA")
        else:
            edge_color = node_colors.get(domain_meta["filter_type"], "#22D3EE")

        g_links.append({
            "source": str(s),
            "target": str(t),
            "name": f"{rel} (Weight: {w:.1f})",
            "color": edge_color if is_edge_active else ("rgba(75, 85, 99, 0.18)" if is_dark else "rgba(203, 213, 225, 0.3)"),
            "particle": 4 if is_edge_active else 0,
            "particleColor": edge_color if is_edge_active else "#666666",
            "tooltip": edge_tooltip
        })

    g_data_json = json.dumps({"nodes": g_nodes, "links": g_links}, ensure_ascii=False)

    force_3d_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background-color: {graph_bg};
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    #3d-graph {{
      width: 100%;
      height: 100%;
    }}
    .guide-badge {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: {'rgba(0, 0, 0, 0.75)' if is_dark else 'rgba(255, 255, 255, 0.92)'};
      color: {'#FFFFFF' if is_dark else '#0F172A'};
      border: 1px solid {border_color};
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 500;
      pointer-events: none;
      z-index: 999;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    .scene-tooltip {{
      position: absolute;
      background: {card_bg} !important;
      color: {text_color} !important;
      border: 1px solid {border_color} !important;
      border-radius: 10px !important;
      padding: 12px 16px !important;
      font-size: 12.5px !important;
      line-height: 1.6 !important;
      box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.4)' if is_dark else 'rgba(0, 0, 0, 0.12)'} !important;
      pointer-events: none !important;
      z-index: 99999 !important;
      max-width: 320px !important;
      white-space: pre-line !important;
      word-break: keep-all !important;
    }}
  </style>
  <!-- Three.js 및 3D Force Graph 공식 검증 CDN -->
  <script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
  <script src="https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js"></script>
</head>
<body>
  <div class="guide-badge">🏷️ 3D 상시 레이블 활성화 | 🖱️ 좌클릭: 360° 회전 | 우클릭: 이동 | 휠: 줌</div>
  <div id="3d-graph"></div>
  <script>
    const gData = {g_data_json};
    const elem = document.getElementById('3d-graph');

    // 순수 HTML5 Canvas를 이용한 텍스트 뱃지 스프라이트 생성기
    function createTextSprite(text, textColor, isSeed, isActive) {{
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 512;
      canvas.height = 128;

      // 배경 둥근 박스
      ctx.fillStyle = isSeed ? 'rgba(211, 47, 47, 0.88)' : (isActive ? '{card_bg}ee' : 'rgba(50, 50, 50, 0.45)');
      const x = 10, y = 10, w = 492, h = 108, r = 24;
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
      ctx.fill();

      // 테두리 선
      ctx.lineWidth = 4;
      ctx.strokeStyle = isSeed ? '#FFD700' : (isActive ? '{accent_color}' : '{border_color}');
      ctx.stroke();

      // 텍스트 출력
      ctx.font = isSeed ? 'bold 44px -apple-system, sans-serif' : 'bold 38px -apple-system, sans-serif';
      ctx.fillStyle = textColor;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, 256, 64);

      const texture = new THREE.CanvasTexture(canvas);
      texture.needsUpdate = true;
      const material = new THREE.SpriteMaterial({{ map: texture, transparent: true, depthWrite: false }});
      const sprite = new THREE.Sprite(material);
      
      // 크기 및 비율 지정
      const scale = isSeed ? 24 : (isActive ? 18 : 12);
      sprite.scale.set(scale * 1.8, scale * 0.45, 1);
      return sprite;
    }}

    const Graph = ForceGraph3D()(elem)
      .backgroundColor('{graph_bg}')
      .graphData(gData)
      .showNavInfo(false)
      .nodeLabel(node => `<div class="scene-tooltip">${{node.tooltip}}</div>`)
      .linkLabel(link => `<div class="scene-tooltip">${{link.tooltip}}</div>`)
      .linkColor('color')
      .linkWidth(link => link.particle > 0 ? 2.0 : 0.4)
      .linkDirectionalParticles('particle')
      .linkDirectionalParticleSpeed(0.008)
      .linkDirectionalParticleWidth(2.5)
      .linkDirectionalParticleColor(link => link.particleColor)
      .nodeThreeObject(node => {{
        const group = new THREE.Group();

        // 1) 3D 구체 노드
        const radius = node.val * 0.6;
        const sphereGeo = new THREE.SphereGeometry(radius, 16, 16);
        const sphereMat = new THREE.MeshBasicMaterial({{
          color: node.color,
          transparent: true,
          opacity: node.is_active ? 0.95 : 0.25
        }});
        const sphere = new THREE.Mesh(sphereGeo, sphereMat);
        group.add(sphere);

        // 2) 구체 상단 텍스트 스프라이트
        const sprite = createTextSprite(node.short_label, node.text_color, node.is_seed, node.is_active);
        sprite.position.y = radius + (node.is_seed ? 8 : 5.5);
        group.add(sprite);

        return group;
      }})
      .nodeThreeObjectExtend(false)
      .onNodeClick(node => {{
        const distance = 120;
        const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
        Graph.cameraPosition(
          {{ x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }},
          node,
          1200
        );
      }});

    // 초기 시점 설정
    setTimeout(() => {{
      Graph.cameraPosition({{ z: 320 }});
    }}, 200);
  </script>
</body>
</html>"""
    return force_3d_html


# =========================================================
# 8. 그래프 렌더러 4: AntV G6 (Alibaba 엔터프라이즈 방사형 뷰)
# =========================================================
def render_antv_g6_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict, domain_meta: dict) -> str:
    """
    선택된 IDE 테마 팔레트가 완벽하게 적용된 AntV G6 방사형(Radial) 엔터프라이즈 그래프 HTML을 생성합니다.
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    node_colors = get_theme_node_color_map(theme, domain_meta)

    parent_type = domain_meta["parent_type"]
    child_type = domain_meta["child_type"]
    rel_mkt = domain_meta["rel_mkt"]
    rel_spec = domain_meta["rel_spec"]
    rel_belongs = domain_meta["rel_belongs"]

    g6_nodes = []
    for node in nodes:
        nid = node["id"]
        ntype = node["type"]
        nname = node["name"]
        is_active = nid in active_nodes
        is_seed = (nid == seed_node_id)
        active_meta = active_nodes.get(nid, {})

        node_tooltip = create_node_plain_tooltip(node, is_active, is_seed, active_meta)
        node_color = node_colors.get(ntype, "#64748B")

        g6_nodes.append({
            "id": nid,
            "label": f"★ {nname}" if is_seed else nname,
            "type": "circle",
            "size": 64 if is_seed else (48 if ntype in [parent_type, child_type] and is_active else (38 if is_active else 26)),
            "style": {
                "fill": node_color if is_active else card_bg,
                "stroke": "#FFD700" if is_seed else (node_color if is_active else border_color),
                "lineWidth": 4 if is_seed else (2.5 if is_active else 1.2),
                "opacity": 1.0 if is_active else 0.28,
                "shadowColor": "#FFD700" if is_seed else (node_color if is_active else "transparent"),
                "shadowBlur": 22 if is_seed else (10 if is_active else 0),
                "cursor": "pointer"
            },
            "labelCfg": {
                "position": "bottom",
                "offset": 7,
                "style": {
                    "fill": "#FFFFFF" if is_dark else "#0F172A",
                    "fontSize": 12 if is_seed else (11 if is_active else 9.5),
                    "fontWeight": "bold" if (is_seed or is_active) else "normal",
                    "background": {
                        "fill": graph_bg,
                        "padding": [2, 6, 2, 6],
                        "radius": 4
                    }
                }
            },
            "tooltip": node_tooltip
        })

    g6_edges = []
    for idx, edge in enumerate(all_evaluated_edges):
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = edge["dynamic_weight"]
        is_active = edge.get("is_active", False)

        s_name = node_dict.get(s, {}).get("name", s)
        t_name = node_dict.get(t, {}).get("name", t)
        edge_tooltip = create_edge_plain_tooltip(edge, is_active, s_name, t_name)

        if rel == rel_mkt:
            edge_color = node_colors.get(domain_meta["mkt_type"], "#C084FC")
        elif rel == rel_spec:
            edge_color = node_colors.get(domain_meta["spec_type"], "#4ADE80")
        elif rel == rel_belongs:
            edge_color = node_colors.get(domain_meta["parent_type"], "#60A5FA")
        else:
            edge_color = node_colors.get(domain_meta["filter_type"], "#22D3EE")

        g6_edges.append({
            "id": f"e_{idx}_{s}_{t}",
            "source": s,
            "target": t,
            "label": f"{rel} ({w:.1f})" if is_active else "",
            "style": {
                "stroke": edge_color if is_active else border_color,
                "lineWidth": 2.6 if is_active else 1.0,
                "opacity": 1.0 if is_active else 0.2,
                "lineDash": None if is_active else [4, 4],
                "endArrow": {
                    "path": "M 0,0 L 8,4 L 8,-4 Z",
                    "fill": edge_color if is_active else border_color,
                    "opacity": 1.0 if is_active else 0.2
                }
            },
            "labelCfg": {
                "autoRotate": True,
                "style": {
                    "fill": "#F8FAFC" if is_dark else "#0F172A",
                    "fontSize": 10,
                    "fontWeight": "bold",
                    "background": {
                        "fill": graph_bg,
                        "padding": [2, 5, 2, 5],
                        "radius": 3
                    }
                }
            },
            "tooltip": edge_tooltip
        })

    g6_data_json = json.dumps({"nodes": g6_nodes, "edges": g6_edges}, ensure_ascii=False)

    antv_g6_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <script src="https://gw.alipayobjects.com/os/lib/antv/g6/4.8.24/dist/g6.min.js"></script>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: {graph_bg};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #mountNode {{
            width: 100%;
            height: 680px;
            position: relative;
        }}
        .g6-tooltip {{
            position: absolute;
            background: {card_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 12.5px;
            line-height: 1.6;
            box-shadow: 0 10px 25px -5px {'rgba(0, 0, 0, 0.4)' if is_dark else 'rgba(0, 0, 0, 0.12)'};
            pointer-events: none;
            z-index: 99999;
            max-width: 320px;
            white-space: pre-line;
            word-break: keep-all;
        }}
    </style>
</head>
<body>
    <div id="mountNode"></div>

    <script>
        const data = {g6_data_json};

        const tooltip = new G6.Tooltip({{
            offsetX: 15,
            offsetY: 15,
            itemTypes: ['node', 'edge'],
            getContent: (e) => {{
                const model = e.item.getModel();
                return model.tooltip || '';
            }},
            className: 'g6-tooltip'
        }});

        const container = document.getElementById('mountNode');
        const width = container.scrollWidth || window.innerWidth;
        const height = 680;

        const graph = new G6.Graph({{
            container: 'mountNode',
            width: width,
            height: height,
            plugins: [tooltip],
            modes: {{
                default: [
                    'drag-canvas',
                    'zoom-canvas',
                    'drag-node',
                    {{
                        type: 'activate-relations',
                        activeState: 'active',
                        inactiveState: 'inactive',
                        resetSelected: true
                    }}
                ]
            }},
            layout: {{
                type: 'radial',
                center: [width / 2, height / 2],
                focusNode: '{seed_node_id}',
                unitRadius: 135,
                linkDistance: 130,
                preventOverlap: true,
                nodeSize: 65,
                strictRadial: false
            }},
            animate: true
        }});

        graph.data(data);
        graph.render();

        // Node click: focus item to center with smooth easing
        graph.on('node:click', (evt) => {{
            const {{ item }} = evt;
            graph.focusItem(item, true, {{
                easing: 'easeCubic',
                duration: 500
            }});
        }});
    </script>
</body>
</html>"""
    return antv_g6_html


# ==========================================
# 9. Main Streamlit Application
# ==========================================
def main():
    st.set_page_config(
        page_title="BigQuery Graph Multi-Domain Explorer",
        page_icon="🚘",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # -------------------------------------------------------------
    # A. 사이드바 최상단: 📂 비즈니스 도메인 및 🎨 10대 IDE 테마 선택기
    # -------------------------------------------------------------
    domain_options = [
        "🚗 자동차 (Automotive)",
        "🛍️ 이커머스 (E-Commerce)",
        "📱 모바일 요금제 (Telco)",
        "🔬 반도체 8대 공정 (Semiconductor)"
    ]

    def on_domain_change():
        new_domain = st.session_state.selected_domain_key
        _, _, new_meta = generate_domain_data(new_domain)
        first_p = new_meta["presets"][0]
        st.session_state.preset_selector_key = first_p["label"]
        st.session_state.user_query_key = first_p["query"]
        st.session_state.intent_key = first_p["intent"]
        st.session_state.seed_node_key = first_p["seed"]
        st.session_state.slider_max_hops = first_p["max_hop"]
        st.session_state.slider_threshold = first_p["weight_threshold"]
        st.session_state.select_filter = first_p["filter"]
        new_tables = get_native_tables(new_meta["id"])
        st.session_state.native_table_selector = list(new_tables.keys())[0]

    def on_preset_change():
        cur_domain = st.session_state.get("selected_domain_key", domain_options[0])
        _, _, cur_meta = generate_domain_data(cur_domain)
        chosen_label = st.session_state.preset_selector_key
        matched_p = next((p for p in cur_meta["presets"] if p["label"] == chosen_label), None)
        if matched_p:
            st.session_state.user_query_key = matched_p["query"]
            st.session_state.intent_key = matched_p["intent"]
            st.session_state.seed_node_key = matched_p["seed"]
            st.session_state.slider_max_hops = matched_p["max_hop"]
            st.session_state.slider_threshold = matched_p["weight_threshold"]
            st.session_state.select_filter = matched_p["filter"]

    # Session State 기본값 초기화 (최초 1회)
    if "selected_domain_key" not in st.session_state:
        st.session_state.selected_domain_key = domain_options[0]
        _, _, init_meta = generate_domain_data(domain_options[0])
        first_p = init_meta["presets"][0]
        st.session_state.preset_selector_key = first_p["label"]
        st.session_state.user_query_key = first_p["query"]
        st.session_state.intent_key = first_p["intent"]
        st.session_state.seed_node_key = first_p["seed"]
        st.session_state.slider_max_hops = first_p["max_hop"]
        st.session_state.slider_threshold = first_p["weight_threshold"]
        st.session_state.select_filter = first_p["filter"]
        init_tables = get_native_tables(init_meta["id"])
        st.session_state.native_table_selector = list(init_tables.keys())[0]

    st.sidebar.markdown("## 📂 Business Domain")
    selected_domain_str = st.sidebar.selectbox(
        "📂 비즈니스 도메인 선택",
        domain_options,
        key="selected_domain_key",
        on_change=on_domain_change,
        help="도메인별로 완전히 다른 지식 그래프 스키마, 온톨로지 공리 및 발화 시나리오로 즉시 전환됩니다."
    )

    # 선택된 도메인 데이터 및 메타데이터 로드
    nodes, edges, domain_meta = generate_domain_data(selected_domain_str)
    node_dict = {n["id"]: n for n in nodes}

    st.sidebar.markdown("## 🎨 UI Theme")
    selected_theme_name = st.sidebar.selectbox(
        "🎨 IDE UI 테마 선택",
        list(THEMES.keys()),
        index=0,
        help="개발자 인기 Light 4종 / Dark 6종 IDE 테마로 전체 UI 배경 및 노드/엣지 배색을 실시간 전환합니다."
    )
    active_theme = THEMES[selected_theme_name]

    # 선택된 테마와 도메인에 맞춰 전체 Streamlit 스타일 동적 주입
    st.markdown(generate_theme_css(active_theme, domain_meta), unsafe_allow_html=True)

    mode_label = "🌙 다크 모드" if active_theme.get("is_dark", True) else "☀️ 라이트 모드"
    st.sidebar.caption(f"도메인: **{domain_meta['name']}** | 테마: **{selected_theme_name}** ({mode_label})")
    st.sidebar.markdown("---")

    # -------------------------------------------------------------
    # B. 발화 시뮬레이션 및 온톨로지 의도 제어
    # -------------------------------------------------------------
    st.sidebar.markdown("### 🗣️ 1. 발화 입력 및 프리셋")
    
    preset_list = domain_meta["presets"]
    preset_labels = [p["label"] for p in preset_list] + ["직접 입력 (Custom Utterance)"]

    if st.session_state.preset_selector_key not in preset_labels:
        st.session_state.preset_selector_key = preset_labels[0]
        on_preset_change()

    selected_preset_label = st.sidebar.selectbox(
        "💬 발화 시나리오 프리셋",
        preset_labels,
        key="preset_selector_key",
        on_change=on_preset_change
    )

    user_query = st.sidebar.text_input(
        "사용자 발화 (Utterance)",
        key="user_query_key"
    )

    st.sidebar.markdown("### 🎯 2. 발화 의도(Intent) & 탐색 시작 노드")
    intent_options = ["INFO_SEARCH", "PURCHASE_INTENT"]
    intent = st.sidebar.radio(
        "추론된 의도 (Inferred Intent)",
        intent_options,
        key="intent_key",
        help=f"• INFO_SEARCH: {domain_meta['rel_mkt']} 가중치 0.1(최우선), {domain_meta['rel_spec']} 0.9(탐색제외)\n• PURCHASE_INTENT: {domain_meta['rel_spec']} 가중치 0.1(최우선), {domain_meta['rel_mkt']} 0.9(탐색제외)"
    )

    theme_node_colors = get_theme_node_color_map(active_theme, domain_meta)
    if intent == "INFO_SEARCH":
        st.sidebar.markdown(f"""
        <div style='background:{active_theme["card_bg"]}; border-left:4px solid {theme_node_colors[domain_meta["mkt_type"]]}; padding:8px; border-radius:4px; font-size:12px; color:{active_theme["text"]};'>
            <b>[가중치 규칙: 정보/혜택 탐색 (INFO_SEARCH)]</b><br/>
            • <code>{domain_meta['rel_mkt']}</code>: <b>0.1 (최우선 활성)</b><br/>
            • <code>{domain_meta['rel_spec']}</code>: <b>0.9 (임계값 초과 시 차단)</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div style='background:{active_theme["card_bg"]}; border-left:4px solid {theme_node_colors[domain_meta["spec_type"]]}; padding:8px; border-radius:4px; font-size:12px; color:{active_theme["text"]};'>
            <b>[가중치 규칙: 실구매/스펙 상담 (PURCHASE_INTENT)]</b><br/>
            • <code>{domain_meta['rel_spec']}</code>: <b>0.1 (최우선 활성)</b><br/>
            • <code>{domain_meta['rel_mkt']}</code>: <b>0.9 (임계값 초과 시 차단)</b>
        </div>
        """, unsafe_allow_html=True)

    seed_candidates = [n["id"] for n in nodes if n["type"] in [domain_meta["parent_type"], domain_meta["child_type"]]]
    if st.session_state.seed_node_key not in seed_candidates:
        st.session_state.seed_node_key = seed_candidates[0]

    seed_node_id = st.sidebar.selectbox(
        "탐색 시작 노드 (Seed Node)",
        seed_candidates,
        key="seed_node_key",
        format_func=lambda x: f"[{node_dict[x]['type']}] {node_dict[x]['name']}"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 3. 온톨로지 탐색 파라미터")
    
    max_hop = st.sidebar.slider(
        "Max Hop (탐색 깊이)",
        min_value=1,
        max_value=3,
        key="slider_max_hops"
    )
    weight_threshold = st.sidebar.slider(
        "Edge Weight Threshold (임계값)",
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        key="slider_threshold",
        help="가중치가 이 임계값 이하인 엣지만 서브그래프 탐색 경로로 활성화됩니다."
    )

    st.sidebar.markdown(f"""
    <div class='weight-guide-box'>
        <b>💡 Edge Weight(가중치) 임계값의 의미:</b><br/>
        1. <b>비용 기반 가중치:</b> 가중치가 <b>0에 가까울수록</b> 현재 의도와의 연관도(우선순위)가 높습니다.<br/>
        2. <b>임계값 ({weight_threshold:.2f} 이하만 통과):</b><br/>
        • <b>낮출 때 (0.1~0.3):</b> 핵심 정보({domain_meta['rel_mkt']} 또는 {domain_meta['rel_spec']})만 엄격 필터링<br/>
        • <b>높일 때 (0.6~1.0):</b> 연관도가 낮은 주변 노드까지 컨텍스트 확장
    </div>
    """, unsafe_allow_html=True)

    filter_options = domain_meta["filter_options"]
    filter_labels_map = domain_meta["filter_options_labels"]
    if st.session_state.select_filter not in filter_options:
        st.session_state.select_filter = filter_options[0]

    filter_val = st.sidebar.selectbox(
        domain_meta["filter_param_name"],
        filter_options,
        key="select_filter",
        format_func=lambda x: filter_labels_map.get(x, x),
        help="[Axiom] 선택된 세그먼트/지역에 귀속된 엔티티 및 관계만 서브그래프로 활성화합니다."
    )

    # -------------------------------------------------------------
    # C. 서브그래프 탐색 실행
    # -------------------------------------------------------------
    active_nodes, active_edges, all_evaluated_edges = explore_subgraph(
        nodes=nodes,
        edges=edges,
        seed_node_id=seed_node_id,
        intent=intent,
        max_hop=max_hop,
        weight_threshold=weight_threshold,
        filter_val=filter_val,
        domain_meta=domain_meta
    )

    # -------------------------------------------------------------
    # D. 메인 헤더 & KPI 메트릭 바
    # -------------------------------------------------------------
    st.markdown(f"## {domain_meta['name']} Semantic Subgraph Explorer")
    st.markdown(
        f"현재 도메인 **`{domain_meta['name']}`**, 발화 의도 **`{intent}`** 및 시작 노드 **`{node_dict[seed_node_id]['name']}`** 기반으로 실시간 온톨로지 공리 탐색이 완료되었습니다. (테마: **`{selected_theme_name}`**)"
    )

    # 메인 화면 가중치 원리 안내 카드
    preferred_rel = domain_meta['rel_mkt'] if intent == 'INFO_SEARCH' else domain_meta['rel_spec']
    deprecate_rel = domain_meta['rel_spec'] if intent == 'INFO_SEARCH' else domain_meta['rel_mkt']
    st.markdown(f"""
    <div class='main-guide-card'>
        <div style='font-weight:700; color:{active_theme["accent"]}; font-size:0.95rem; margin-bottom:6px;'>
            🧠 온톨로지 동적 가중치 탐색 원리 (Intent-Driven Dynamic Traversal)
        </div>
        <div style='display:flex; flex-wrap:wrap; gap:16px;'>
            <div style='flex:1; min-width:280px;'>
                <b>1. 비용 기반 가중치 (Cost-based Weight):</b><br/>
                온톨로지 그래프에서는 <b>가중치 값이 0에 가까울수록</b> 사용자 의도와의 연관도(우선순위)가 높음을 뜻합니다.
                현재 의도(<code>{intent}</code>)에 따라 <b>{preferred_rel}</b> 관계는 <b>0.1</b>로 최우선 배정되고, <b>{deprecate_rel}</b> 관계는 <b>0.9</b>로 후순위 처리됩니다.
            </div>
            <div style='flex:1; min-width:280px;'>
                <b>2. 임계값(Threshold = {weight_threshold:.2f}) 동작:</b><br/>
                현재 설정된 임계값 <b>이하</b>의 엣지만 서브그래프 경로에 포함됩니다. 임계값을 낮추면 노이즈 없는 핵심 서브그래프만 추출되고, 임계값을 높이면 주변 연관 데이터까지 폭넓게 탐색합니다.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Active Subgraph Nodes</div>
            <div class='metric-value'>{len(active_nodes)} <span style='font-size:0.9rem; opacity:0.85;'>/ {len(nodes)}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Active Traverse Edges</div>
            <div class='metric-value'>{len(active_edges)} <span style='font-size:0.9rem; opacity:0.85;'>/ {len(edges)}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Query Execution Time</div>
            <div class='metric-value'>12.4 <span style='font-size:0.9rem; opacity:0.85;'>ms (BigQuery)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        subgraph_coverage = round((len(active_nodes) / len(nodes)) * 100, 1)
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Context Density Score</div>
            <div class='metric-value'>{subgraph_coverage}% <span style='font-size:0.9rem; color:{theme_node_colors[domain_meta["spec_type"]]};'>Filtered</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드 Expander
    with st.expander(f"💡 [{domain_meta['name']}] 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드", expanded=False):
        st.markdown(f"""
        #### 📌 엣지(Edge) 관계별 비즈니스 레이어 구분 ({domain_meta['name']})
        
        | 구분 | `{domain_meta['rel_mkt']}` (마케팅 & 프로모션 & 소구점) | `{domain_meta['rel_spec']}` (실구매 & 상세 스펙 & 제원) |
        |---|---|---|
        | **핵심 질문** | **"왜 이 상품/요금제를 선택해야 하는가?"** (Why to Choose) | **"실제 어떤 사양과 제원이 들어있는가?"** (What is Inside) |
        | **출발 노드** | `{domain_meta['parent_type']}` (상위 브랜드/카테고리/패밀리) | `{domain_meta['child_type']}` (상세 모델/SKU/요금제 코드) |
        | **도착 노드** | `{domain_meta['mkt_type']}` (기획전, 소구점, 부가 혜택) | `{domain_meta['spec_type']}` (하드웨어 제원, 소재, QoS 스펙) |
        | **적합한 의도** | **정보/혜택 탐색 (`INFO_SEARCH`)** | **실구매/스펙 상담 (`PURCHASE_INTENT`)** |
        
        ---
        
        #### 🎯 발화 의도(Intent)에 따른 가변 컨텍스트 제어 및 LLM 연계 원리
        - **정보/혜택 탐색 (`INFO_SEARCH`):** 복잡한 세부 제원을 배제하고 `{domain_meta['rel_mkt']}` 관계 가중치를 **0.1 (최우선)**로 낮춰 핵심 소구점을 LLM 주입 컨텍스트로 전달합니다.
        - **실구매/스펙 상담 (`PURCHASE_INTENT`):** 모호한 마케팅 문구를 배제하고 `{domain_meta['rel_spec']}` 관계 가중치를 **0.1 (최우선)**로 낮춰 정확한 스펙 데이터만 LLM 주입 컨텍스트로 정밀 전달합니다.
        """)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # E. 메인 패널 수직 배치 (Full Width Vertical Layout)
    # -------------------------------------------------------------
    
    # =============================================================
    # 1. [상단 영역] Interactive Knowledge Graph Visualization (Full Width)
    # =============================================================
    st.markdown("### 🕸️ Interactive Knowledge Graph Visualization")

    col_rend1, col_rend2 = st.columns([1.3, 2.7])
    with col_rend1:
        renderer_options = [
            "1. PyVis (2D Physics 물리 엔진)",
            "2. Cytoscape.js (구조적 엔지니어링 뷰)",
            "3. 3D Force Graph (WebGL 3D 우주 궤도 뷰)",
            "4. AntV G6 (Alibaba 엔터프라이즈 방사형 뷰)"
        ]
        selected_renderer = st.selectbox(
            "📊 그래프 렌더링 엔진 선택",
            renderer_options,
            index=0,
            help="동일한 온톨로지 서브그래프 데이터를 4가지 최신 시각화 엔진(2D 물리, 엔지니어링, 3D WebGL 우주, 엔터프라이즈 방사형)으로 전환하여 비교합니다."
        )
    with col_rend2:
        if "PyVis" in selected_renderer:
            st.info("⚡ **PyVis (Vis.js Physics)**: ForceAtlas2 기반 2D 물리 시뮬레이션으로 노드가 유기적으로 넓게 퍼지며 자유로운 드래그와 물리 반동 효과를 제공합니다.")
        elif "Cytoscape" in selected_renderer:
            st.info("📐 **Cytoscape.js (COSE Layout)**: 생물정보학 및 네트워크 공학 표준 계층형 그래프 엔진으로 안정적인 구조적 위상과 베지어 곡선 엣지를 제공합니다.")
        elif "3D Force" in selected_renderer:
            st.info("🚀 **3D Force Graph (Three.js / WebGL)**: 3차원 우주 궤도 공간에서 노드가 3D 구체로 회전하며, 활성 탐색 경로를 따라 빛나는 에너지 입자(Particle)가 실시간으로 흐릅니다.")
        else:
            st.info("🎨 **AntV G6 (Alibaba Enterprise Radial)**: 알리바바 엔터프라이즈 방사형(Radial) 위상 레이아웃으로 시작 노드 중심 1-Hop/2-Hop 노드 포커싱 및 글로우(Glow) 효과를 제공합니다.")

    st.markdown(f"""
    <div class='legend-box'>
        <span class='badge badge-node-parent'>● {domain_meta['parent_label']}</span>
        <span class='badge badge-node-child'>● {domain_meta['child_label']}</span>
        <span class='badge badge-node-spec'>● {domain_meta['spec_label']}</span>
        <span class='badge badge-node-marketing'>● {domain_meta['mkt_label']}</span>
        <span class='badge badge-node-filter'>● {domain_meta['filter_label']}</span>
        <span style='font-size:0.75rem; opacity:0.85; margin-left:auto;'>★ 노란 테두리: 시작 노드 | 반투명: 비활성 노드</span>
    </div>
    """, unsafe_allow_html=True)

    if "PyVis" in selected_renderer:
        graph_html = render_pyvis_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme, domain_meta)
        components.html(graph_html, height=710, scrolling=False)
        st.caption("💡 PyVis 팁: 마우스 휠로 줌인/줌아웃하고, 노드를 드래그하여 자유롭게 배치할 수 있습니다. 마우스 호버 시 카드형 툴팁이 표시됩니다.")
    elif "Cytoscape" in selected_renderer:
        cytoscape_html = render_cytoscape_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme, domain_meta)
        components.html(cytoscape_html, height=710, scrolling=False)
        st.caption("💡 Cytoscape.js 팁: 배경을 드래그하여 팬(Pan) 이동하고, 노드/엣지 위에 마우스를 올리면 상세 카드 툴팁이 나타납니다.")
    elif "3D Force" in selected_renderer:
        force_3d_html = render_3d_force_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme, domain_meta)
        components.html(force_3d_html, height=710, scrolling=False)
        st.caption("💡 3D Force Graph 팁: 좌클릭 드래그로 360도 회전, 우클릭 드래그로 팬(Pan) 이동, 마우스 휠로 줌인/줌아웃할 수 있습니다. 노드 클릭 시 카메라가 해당 노드로 부드럽게 이동합니다.")
    else:
        antv_g6_html = render_antv_g6_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme, domain_meta)
        components.html(antv_g6_html, height=710, scrolling=False)
        st.caption("💡 AntV G6 팁: 노드 위에 마우스를 올리면 연결된 엣지만 활성화(Focus)되며, 노드 클릭 시 해당 노드를 화면 중앙으로 이동시킵니다.")

    st.markdown(f"<div style='margin-top: 24px; margin-bottom: 24px;'><hr style='border:0; border-top:1px solid {active_theme['border']};'/></div>", unsafe_allow_html=True)

    # =============================================================
    # 2. [하단 영역] Dynamic Cypher/GQL Query & Grounding Result (Full Width)
    # =============================================================
    st.markdown("### ⚡ Dynamic Cypher/GQL Query & Grounding Result")

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Dynamic GQL Query",
        "📜 BigQuery Property Graph DDL",
        "🕸️ Filtered Subgraph",
        "🗄️ BigQuery Native Tables"
    ])

    with tab1:
        gql_standard, gql_graph_table = generate_bigquery_gql(seed_node_id, intent, max_hop, weight_threshold, filter_val, node_dict, domain_meta)

        st.markdown(f"#### 1. BigQuery GQL 표준 쿼리 ({domain_meta['name']})")
        st.code(gql_standard, language="sql")

        st.markdown(f"#### 2. BigQuery `GRAPH_TABLE` 멀티홉 탐색 쿼리 (Dynamic GoogleSQL GQL)")
        st.code(gql_graph_table, language="sql")

        with st.expander("🔍 openCypher 호환 표준 쿼리 보기"):
            cypher_query = f"""// openCypher Standard Query ({domain_meta['name']})
MATCH p = (start:{node_dict[seed_node_id]['type']} {{id: '{seed_node_id}'}})-[r*1..{max_hop}]-(target)
WHERE ALL(e IN relationships(p) WHERE e.weight <= {weight_threshold:.2f})
RETURN 
    p, 
    target.name AS target_name, 
    target.type AS target_type, 
    reduce(cost = 0, e IN relationships(p) | cost + e.weight) AS total_cost
ORDER BY 
    total_cost ASC;"""
            st.code(cypher_query, language="sql")

        st.markdown("<hr style='margin: 16px 0;'/>", unsafe_allow_html=True)

        context_payload, llm_response, specs, mkts, children = build_llm_context_and_response(
            intent=intent,
            seed_node_id=seed_node_id,
            active_nodes=active_nodes,
            active_edges=active_edges,
            node_dict=node_dict,
            user_query=user_query,
            domain_meta=domain_meta
        )

        st.markdown("#### 💬 LLM Response Simulation (RAG 기반 응답)")
        st.info(llm_response)

        st.markdown("#### 📦 LLM 주입 컨텍스트 (Injected Grounding Prompt Context)")
        st.json(context_payload)

    with tab2:
        st.caption(f"📜 Google Cloud BigQuery에서 관계형 테이블을 지식 그래프(Property Graph)로 인덱싱 및 정의하는 공식 `CREATE PROPERTY GRAPH` DDL 스크립트입니다. ({domain_meta['name']})")
        
        bq_ddl = generate_bigquery_ddl(domain_meta["name"])
        st.code(bq_ddl, language="sql")

        st.info("""💡 **BigQuery Property Graph DDL 구문 핵심 가이드**:
• **`NODE TABLES`**: 그래프 엔티티 노드로 변환할 물리 마스터 테이블(`dim_*`)과 고유 식별자 `KEY`, 노드 라벨 `LABEL`, 노출 속성 `PROPERTIES`를 정의합니다.
• **`EDGE TABLES`**: 엔티티 간 관계를 정의하는 매핑 테이블(`rel_*`)과 시작 노드(`SOURCE KEY REFERENCES`), 도착 노드(`DESTINATION KEY REFERENCES`), 관계 라벨 `LABEL` 및 비용 가중치(`weight_*`) 속성을 매핑합니다.""")

    with tab3:
        st.caption("🔍 사용자 발화 의도(Intent) 및 가중치 임계값 필터링을 거쳐 LLM 컨텍스트로 주입되는 가변 서브그래프 결과입니다.")

        st.markdown("#### 1. 활성화된 노드 목록 (Active Subgraph Nodes)")
        node_table_rows = []
        for nid, meta in active_nodes.items():
            n = node_dict.get(nid, {})
            node_table_rows.append({
                "Node ID": nid,
                "Entity Name": n.get("name"),
                "Type": n.get("type"),
                "Hop Distance": meta.get("hop"),
                "Traverse Cost": meta.get("cost"),
                "Relevance Score": meta.get("relevance")
            })
        if node_table_rows:
            df_nodes = pd.DataFrame(node_table_rows).sort_values(by=["Hop Distance", "Traverse Cost"])
            st.dataframe(df_nodes, hide_index=True)
        else:
            st.warning("조건에 일치하는 활성 노드가 없습니다.")

        st.markdown("#### 2. 활성화된 엣지 목록 (Active Traverse Edges)")
        edge_table_rows = []
        for e in active_edges:
            edge_table_rows.append({
                "Source Node": node_dict.get(e["source"], {}).get("name", e["source"]),
                "Relation (Edge)": e["relation"],
                "Target Node": node_dict.get(e["target"], {}).get("name", e["target"]),
                "Dynamic Weight": e["dynamic_weight"],
                "Description": e.get("desc", "")
            })
        if edge_table_rows:
            df_edges = pd.DataFrame(edge_table_rows)
            st.dataframe(df_edges, hide_index=True)
        else:
            st.warning("조건에 일치하는 활성 엣지가 없습니다.")

    with tab4:
        st.caption(f"🏢 BigQuery Property Graph(`{domain_meta['bq_dataset']}`)의 기반이 되는 물리적 원본 관계형 테이블(Relational Tables)입니다.")

        native_tables = get_native_tables(domain_meta["id"])
        native_tbl_keys = list(native_tables.keys())
        if st.session_state.get("native_table_selector") not in native_tbl_keys:
            st.session_state.native_table_selector = native_tbl_keys[0]

        selected_tbl_name = st.selectbox(
            "📋 조회할 BigQuery 원본 테이블 선택",
            native_tbl_keys,
            key="native_table_selector"
        )

        df_native = native_tables[selected_tbl_name]
        st.dataframe(df_native, hide_index=True)

        is_node_table = selected_tbl_name.startswith("dim_")
        graph_binding_type = "NODE TABLE (엔티티 노드)" if is_node_table else "EDGE TABLE (관계 엣지)"
        st.info(f"💡 **Property Graph 매핑 안내**: 이 `{selected_tbl_name.split()[0]}` 테이블은 BigQuery `CREATE PROPERTY GRAPH` DDL에서 **{graph_binding_type}**로 바인딩되어 지식 그래프를 구성합니다.")


if __name__ == "__main__":
    main()
