"""
Google Cloud BigQuery Graph & 시맨틱 온톨로지 탐색기 (Vehicle Knowledge Graph)
Streamlit + PyVis / Cytoscape.js 듀얼 엔진 및 10대 IDE 테마(Light 4종 + Dark 6종) 실시간 전환 애플리케이션 (단일 파일: app.py)
"""

import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network
import pandas as pd
import json

# ==========================================
# 0. 10대 개발자 인기 IDE 테마 팔레트 정의 (Light 4종 + Dark 6종)
# ==========================================
THEMES = {
    # --- [Light Themes] ---
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
    # --- [Dark Themes] ---
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


def generate_theme_css(theme: dict) -> str:
    """
    선택된 IDE 테마 팔레트에 따라 Streamlit 전체 UI의 배경, 사이드바, 카드, 텍스트 스타일 및
    Prism.js 코드 블록 구문 강조(Syntax Highlighting)를 최적화하여 동적 주입합니다.
    """
    is_dark = theme.get("is_dark", True)
    bg = theme["bg"]
    sidebar_bg = theme["sidebar_bg"]
    card_bg = theme["card_bg"]
    text = theme["text"]
    accent = theme["accent"]
    border = theme["border"]
    node_colors = theme["node_colors"]

    # Prism.js 구문 강조 색상 (Dark / Light 모드별 최적화)
    if is_dark:
        code_bg = sidebar_bg
        token_keyword = "#C678DD"   # Pink / Purple
        token_string = "#98C379"    # Soft Green
        token_comment = "#7F848E"   # Muted Gray
        token_number = "#D19A66"    # Orange
        token_function = "#61AFEF"  # Cyan / Blue
        token_operator = "#56B6C2"  # Teal
        token_punct = "#ABB2BF"     # Light Gray
    else:
        code_bg = "#F6F8FA" if bg == "#FFFFFF" else "#EAEAEB"
        token_keyword = "#005CC5"   # Deep Blue
        token_string = "#22863A"    # Forest Green
        token_comment = "#6A737D"   # Slate Gray
        token_number = "#E36209"    # Warm Orange
        token_function = "#6F42C1"  # Purple
        token_operator = "#D73A49"  # Crimson Red
        token_punct = "#24292F"     # Dark Slate

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

    /* 4. 입력 위젯 (Radio, Selectbox, TextInput, Slider) */
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

    /* 7. 범례 박스 및 테마별 노드 컬러 배지 */
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
    .badge-node-family {{ background-color: {node_colors['FamilyCar']}{'30' if is_dark else '18'} !important; color: {node_colors['FamilyCar']} !important; border: 1px solid {node_colors['FamilyCar']} !important; }}
    .badge-node-model {{ background-color: {node_colors['ModelCode']}{'30' if is_dark else '18'} !important; color: {node_colors['ModelCode']} !important; border: 1px solid {node_colors['ModelCode']} !important; }}
    .badge-node-spec {{ background-color: {node_colors['SpecItem']}{'30' if is_dark else '18'} !important; color: {node_colors['SpecItem']} !important; border: 1px solid {node_colors['SpecItem']} !important; }}
    .badge-node-marketing {{ background-color: {node_colors['MarketingInfo']}{'30' if is_dark else '18'} !important; color: {node_colors['MarketingInfo']} !important; border: 1px solid {node_colors['MarketingInfo']} !important; }}
    .badge-node-region {{ background-color: {node_colors['Region']}{'30' if is_dark else '18'} !important; color: {node_colors['Region']} !important; border: 1px solid {node_colors['Region']} !important; }}

    /* 8. Expander, 탭, 데이터프레임 */
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

    /* 9. Prism.js 코드 블록 구문 강조 (Syntax Highlighting) 명시적 복원 */
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


# ==========================================
# 1. 지식 그래프 스키마 및 Mock Data 생성
# ==========================================
def generate_graph_data():
    """
    온톨로지 스키마에 정의된 노드 및 관계를 기반으로 Mock Graph 데이터를 생성합니다.
    """
    nodes = [
        # --- FamilyCar 노드 ---
        {
            "id": "FC_SORENTO",
            "name": "소렌토 (Sorento)",
            "type": "FamilyCar",
            "desc": "기아 대표 중형 패밀리 SUV",
            "attributes": {"segment": "Midsize SUV", "manufacturer": "Kia", "seats": "5/6/7인승"}
        },
        {
            "id": "FC_SANTAFE",
            "name": "싼타페 (Santa Fe)",
            "type": "FamilyCar",
            "desc": "현대 대표 도심형/아웃도어 패밀리 SUV",
            "attributes": {"segment": "Midsize SUV", "manufacturer": "Hyundai", "seats": "5/6/7인승"}
        },

        # --- ModelCode 노드 (소렌토) ---
        {
            "id": "MC_MQ4_KR",
            "name": "MQ4 (소렌토 가솔린/디젤 내수)",
            "type": "ModelCode",
            "desc": "4세대 소렌토 국내 내연기관 모델",
            "attributes": {"generation": "4th Gen", "powertrain": "2.5T / 2.2D", "market": "KR"}
        },
        {
            "id": "MC_MQ4_HEV_KR",
            "name": "MQ4 HEV (소렌토 하이브리드 내수)",
            "type": "ModelCode",
            "desc": "4세대 소렌토 국내 터보 하이브리드 모델",
            "attributes": {"generation": "4th Gen", "powertrain": "1.6T HEV", "market": "KR"}
        },
        {
            "id": "MC_MQ4_US",
            "name": "MQ4a (소렌토 북미 수출형)",
            "type": "ModelCode",
            "desc": "소렌토 북미 조지아 공장 생산형",
            "attributes": {"generation": "4th Gen", "powertrain": "2.5T / 1.6T HEV", "market": "US"}
        },

        # --- ModelCode 노드 (싼타페) ---
        {
            "id": "MC_MX5_KR",
            "name": "MX5 (싼타페 가솔린 내수)",
            "type": "ModelCode",
            "desc": "5세대 디 올 뉴 싼타페 국내 가솔린 모델",
            "attributes": {"generation": "5th Gen", "powertrain": "2.5T", "market": "KR"}
        },
        {
            "id": "MC_MX5_HEV_KR",
            "name": "MX5 HEV (싼타페 하이브리드 내수)",
            "type": "ModelCode",
            "desc": "5세대 디 올 뉴 싼타페 국내 터보 하이브리드 모델",
            "attributes": {"generation": "5th Gen", "powertrain": "1.6T HEV", "market": "KR"}
        },
        {
            "id": "MC_MX5_US",
            "name": "MX5a (싼타페 북미 수출형)",
            "type": "ModelCode",
            "desc": "싼타페 북미 수출 및 현지 생산형",
            "attributes": {"generation": "5th Gen", "powertrain": "2.5T AWD", "market": "US"}
        },

        # --- Region 노드 ---
        {
            "id": "REG_KR",
            "name": "KR (대한민국)",
            "type": "Region",
            "desc": "국내 내수 시장 (K-Certification / 국내 보증)",
            "attributes": {"code": "KR", "currency": "KRW", "ev_subsidy": "적용"}
        },
        {
            "id": "REG_US",
            "name": "US (미국)",
            "type": "Region",
            "desc": "북미 시장 (EPA / IIHS 규격)",
            "attributes": {"code": "US", "currency": "USD", "safety_std": "FMVSS"}
        },
        {
            "id": "REG_SEA",
            "name": "SEA (동남아)",
            "type": "Region",
            "desc": "동남아 아세안 시장 (우핸들/열대 특화)",
            "attributes": {"code": "SEA", "currency": "USD/Local", "climate": "Tropical"}
        },

        # --- SpecItem 노드 (사양 / 옵션) ---
        {
            "id": "SPEC_HEV_16T",
            "name": "1.6T 터보 하이브리드",
            "type": "SpecItem",
            "desc": "최고출력 245ps(합산), 복합연비 15.7km/L 하이브리드 파워트레인",
            "attributes": {"category": "Powertrain", "efficiency": "15.7 km/L", "power": "245 ps"}
        },
        {
            "id": "SPEC_GAS_25T",
            "name": "2.5T 가솔린 터보",
            "type": "SpecItem",
            "desc": "최고출력 281ps, 최대토크 43.0kgf·m 스마트스트림 G2.5T",
            "attributes": {"category": "Powertrain", "power": "281 ps", "torque": "43.0 kgf·m"}
        },
        {
            "id": "SPEC_AWD",
            "name": "전자식 AWD (4륜구동)",
            "type": "SpecItem",
            "desc": "지형 반응 모드(터레인 모드: Snow/Mud/Sand) 연동 전자식 4WD",
            "attributes": {"category": "Drivetrain", "terrain_mode": "Auto/Snow/Mud/Sand"}
        },
        {
            "id": "SPEC_HUD",
            "name": "HUD (헤드업 디스플레이)",
            "type": "SpecItem",
            "desc": "10인치 윈드실드 타입 고해상도 그래픽 HUD",
            "attributes": {"category": "Convenience", "size": "10 inch", "ad_display": "ADAS 연동"}
        },
        {
            "id": "SPEC_DRIVEWISE",
            "name": "드라이브 와이즈 (고속도로 주행보조 2)",
            "type": "SpecItem",
            "desc": "HDA2, 전방 충돌방지 보조, 스마트 크루즈(정차&재출발) 패키지",
            "attributes": {"category": "Safety / ADAS", "level": "Level 2+", "features": "차로변경보조 포함"}
        },
        {
            "id": "SPEC_BUILTINCAM2",
            "name": "빌트인 캠 2 (QHD)",
            "type": "SpecItem",
            "desc": "전후방 QHD 고화질 녹화, 음성녹음 및 증강현실 내비게이션 지원",
            "attributes": {"category": "Electronics", "resolution": "QHD", "audio": "지원"}
        },
        {
            "id": "SPEC_PANORAMA_SUNROOF",
            "name": "파노라마 선루프",
            "type": "SpecItem",
            "desc": "와이드 오픈 파노라마 선루프 & 전동 롤 블라인드",
            "attributes": {"category": "Exterior / Interior", "type": "Wide Electric"}
        },
        {
            "id": "SPEC_POWER_TAILGATE",
            "name": "스마트 파워 테일게이트",
            "type": "SpecItem",
            "desc": "스마트키 소지 후 접근 시 자동 오픈 및 높이 조절 메모리 기능",
            "attributes": {"category": "Convenience", "auto_open": "지원"}
        },

        # --- MarketingInfo 노드 (마케팅 / KSP 정보) ---
        {
            "id": "MKT_2025_RELEASE",
            "name": "2025 신형 출시 일정 & 사전계약 혜택",
            "type": "MarketingInfo",
            "desc": "2025년형 페이스리프트 출시 일정 확정, 얼리버드 전용 금융 프로모션 및 바우처 증정",
            "attributes": {"target_date": "2025 Q3", "benefit": "연 2.9% 저금리 & 50만원 바우처"}
        },
        {
            "id": "MKT_FAMILY_SPACE",
            "name": "동급 최고 패밀리 SUV 공간성 & 3열 독립시트",
            "type": "MarketingInfo",
            "desc": "동급 최장 휠베이스로 넉넉한 2열 레그룸 및 3열 폴딩 시 대용량 차박 트렁크 공간 제공",
            "attributes": {"wheelbase": "2,815 mm", "trunk_capacity": "최대 2,044L (폴딩 시)"}
        },
        {
            "id": "MKT_HEV_BENEFIT",
            "name": "하이브리드 친환경차 세제혜택 & 복합연비 15.7km/L",
            "type": "MarketingInfo",
            "desc": "개별소비세/취득세 최대 143만원 감면 및 공영주차장/혼잡통행료 50% 할인 혜택",
            "attributes": {"tax_discount": "최대 143만원", "parking_discount": "50% 감면"}
        },
        {
            "id": "MKT_SAFETY_TSP",
            "name": "북미 IIHS 톱 세이프티 픽 플러스(TSP+) 획득",
            "type": "MarketingInfo",
            "desc": "미국 고속도로 안전보험협회(IIHS) 충돌 평가 최고 등급 획득 및 10-에어백 기본 탑재",
            "attributes": {"rating": "IIHS Top Safety Pick+", "airbags": "10 에어백"}
        },
        {
            "id": "MKT_DESIGN_STARMAP",
            "name": "시그니처 스타맵 라이팅 & 파노라믹 커브드 디스플레이",
            "type": "MarketingInfo",
            "desc": "기아의 새로운 패밀리룩 수직형 헤드램프 및 12.3인치 듀얼 파노라믹 디스플레이 적용",
            "attributes": {"cluster": "12.3인치 파노라믹", "exterior": "수직형 스타맵 DRL"}
        },
        {
            "id": "MKT_SANTAFE_HLIGHT",
            "name": "H-라이트 디자인 & 테라스 콘셉트 대형 테일게이트",
            "type": "MarketingInfo",
            "desc": "현대 엠블럼 재해석 H-시그니처 램프와 아웃도어 라이프스타일에 최적화된 테일게이트 공간",
            "attributes": {"concept": "Open for More (Terrace Tailgate)", "exterior": "H-Light"}
        }
    ]

    # --- 온톨로지 관계 (Edges) 기본 정의 ---
    edges = [
        # --- BELONGS_TO: ModelCode -> FamilyCar ---
        {"source": "MC_MQ4_KR", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 모델 라인업 귀속"},
        {"source": "MC_MQ4_HEV_KR", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 하이브리드 라인업 귀속"},
        {"source": "MC_MQ4_US", "target": "FC_SORENTO", "relation": "BELONGS_TO", "desc": "소렌토 북미 모델 라인업 귀속"},
        {"source": "MC_MX5_KR", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 모델 라인업 귀속"},
        {"source": "MC_MX5_HEV_KR", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 하이브리드 라인업 귀속"},
        {"source": "MC_MX5_US", "target": "FC_SANTAFE", "relation": "BELONGS_TO", "desc": "싼타페 북미 모델 라인업 귀속"},

        # --- AVAILABLE_IN: ModelCode -> Region ---
        {"source": "MC_MQ4_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
        {"source": "MC_MQ4_HEV_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
        {"source": "MC_MQ4_US", "target": "REG_US", "relation": "AVAILABLE_IN", "desc": "미국 시장 판매"},
        {"source": "MC_MX5_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
        {"source": "MC_MX5_HEV_KR", "target": "REG_KR", "relation": "AVAILABLE_IN", "desc": "대한민국 내수 판매"},
        {"source": "MC_MX5_US", "target": "REG_US", "relation": "AVAILABLE_IN", "desc": "미국 시장 판매"},

        # --- APPLIES_SPEC: ModelCode -> SpecItem ---
        {"source": "MC_MQ4_KR", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "2.5T 가솔린 터보 기본 탑재"},
        {"source": "MC_MQ4_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "선택 사양 전자식 4WD"},
        {"source": "MC_MQ4_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "선택 사양 헤드업 디스플레이"},
        {"source": "MC_MQ4_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "선택 사양 드라이브 와이즈"},
        {"source": "MC_MQ4_KR", "target": "SPEC_POWER_TAILGATE", "relation": "APPLIES_SPEC", "desc": "기본 사양 파워 테일게이트"},

        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_HEV_16T", "relation": "APPLIES_SPEC", "desc": "1.6T 터보 하이브리드 파워트레인"},
        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "e-AWD 전기모터 보조 4륜구동"},
        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "선택 사양 10인치 HUD"},
        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "기본/선택 드라이브 와이즈"},
        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_BUILTINCAM2", "relation": "APPLIES_SPEC", "desc": "선택 사양 QHD 빌트인 캠 2"},
        {"source": "MC_MQ4_HEV_KR", "target": "SPEC_PANORAMA_SUNROOF", "relation": "APPLIES_SPEC", "desc": "선택 사양 파노라마 선루프"},

        {"source": "MC_MQ4_US", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "북미 2.5T 가솔린 터보 기본"},
        {"source": "MC_MQ4_US", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "북미 X-Line 패키지 4WD"},
        {"source": "MC_MQ4_US", "target": "SPEC_PANORAMA_SUNROOF", "relation": "APPLIES_SPEC", "desc": "북미 프리미엄 트림 선루프"},

        {"source": "MC_MX5_KR", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "스마트스트림 G2.5T 탑재"},
        {"source": "MC_MX5_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "HTRAC 전자식 AWD"},
        {"source": "MC_MX5_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "컴바이너/윈드실드 HUD"},
        {"source": "MC_MX5_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "현대 스마트센스 패키지"},

        {"source": "MC_MX5_HEV_KR", "target": "SPEC_HEV_16T", "relation": "APPLIES_SPEC", "desc": "1.6T 터보 하이브리드 탑재"},
        {"source": "MC_MX5_HEV_KR", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "HTRAC 하이브리드 4WD"},
        {"source": "MC_MX5_HEV_KR", "target": "SPEC_HUD", "relation": "APPLIES_SPEC", "desc": "헤드업 디스플레이"},
        {"source": "MC_MX5_HEV_KR", "target": "SPEC_DRIVEWISE", "relation": "APPLIES_SPEC", "desc": "스마트센스 (HDA2 포함)"},
        {"source": "MC_MX5_HEV_KR", "target": "SPEC_BUILTINCAM2", "relation": "APPLIES_SPEC", "desc": "빌트인 캠 2 증강현실"},
        {"source": "MC_MX5_HEV_KR", "target": "SPEC_PANORAMA_SUNROOF", "relation": "APPLIES_SPEC", "desc": "듀얼 와이드 선루프"},

        {"source": "MC_MX5_US", "target": "SPEC_GAS_25T", "relation": "APPLIES_SPEC", "desc": "북미 2.5T 가솔린 사양"},
        {"source": "MC_MX5_US", "target": "SPEC_AWD", "relation": "APPLIES_SPEC", "desc": "북미 표준 HTRAC AWD"},

        # --- HAS_KSP: ModelCode / FamilyCar -> MarketingInfo ---
        {"source": "FC_SORENTO", "target": "MKT_2025_RELEASE", "relation": "HAS_KSP", "desc": "소렌토 신형 출시 일정 & 사전계약"},
        {"source": "FC_SORENTO", "target": "MKT_FAMILY_SPACE", "relation": "HAS_KSP", "desc": "소렌토 동급 최대 실내공간 강조"},
        {"source": "FC_SORENTO", "target": "MKT_DESIGN_STARMAP", "relation": "HAS_KSP", "desc": "소렌토 스타맵 시그니처 디자인 KSP"},
        {"source": "MC_MQ4_HEV_KR", "target": "MKT_HEV_BENEFIT", "relation": "HAS_KSP", "desc": "소렌토 하이브리드 세제혜택 & 연비"},
        {"source": "MC_MQ4_US", "target": "MKT_SAFETY_TSP", "relation": "HAS_KSP", "desc": "소렌토 북미 IIHS 최고 안전등급"},

        {"source": "FC_SANTAFE", "target": "MKT_SANTAFE_HLIGHT", "relation": "HAS_KSP", "desc": "싼타페 H-라이트 & 테라스 테일게이트"},
        {"source": "FC_SANTAFE", "target": "MKT_FAMILY_SPACE", "relation": "HAS_KSP", "desc": "싼타페 3열 대형 실내공간"},
        {"source": "MC_MX5_HEV_KR", "target": "MKT_HEV_BENEFIT", "relation": "HAS_KSP", "desc": "싼타페 하이브리드 친환경 혜택"},
        {"source": "MC_MX5_US", "target": "MKT_SAFETY_TSP", "relation": "HAS_KSP", "desc": "싼타페 북미 IIHS 안전등급"}
    ]

    return nodes, edges


# =========================================================
# 2. 온톨로지 동적 가중치 규칙 및 서브그래프 탐색 알고리즘
# =========================================================
def get_edge_weight(relation: str, intent: str) -> float:
    """
    온톨로지 공리 [Weight Rule]에 따라 의도(Intent)별 가중치를 산출합니다.
    """
    if intent == "INFO_SEARCH":
        if relation == "HAS_KSP":
            return 0.1
        elif relation == "BELONGS_TO":
            return 0.2
        elif relation == "AVAILABLE_IN":
            return 0.3
        elif relation == "APPLIES_SPEC":
            return 0.9
        else:
            return 0.5
    elif intent == "PURCHASE_INTENT":
        if relation == "APPLIES_SPEC":
            return 0.1
        elif relation == "BELONGS_TO":
            return 0.2
        elif relation == "AVAILABLE_IN":
            return 0.3
        elif relation == "HAS_KSP":
            return 0.9
        else:
            return 0.5
    else:
        return 0.5


def explore_subgraph(nodes, edges, seed_node_id: str, intent: str, max_hop: int, weight_threshold: float, region_filter: str):
    """
    시드 노드로부터 시작하여 가중치 임계값, Max Hop, 지역 필터를 만족하는 활성 서브그래프를 탐색합니다.
    """
    G = nx.Graph()
    node_dict = {n["id"]: n for n in nodes}

    for n in nodes:
        G.add_node(n["id"], **n)

    all_evaluated_edges = []
    for edge in edges:
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = get_edge_weight(rel, intent)

        valid_region = True
        if region_filter != "ALL":
            s_node = node_dict.get(s, {})
            t_node = node_dict.get(t, {})
            
            if s_node.get("type") == "Region" and s_node.get("attributes", {}).get("code") != region_filter:
                valid_region = False
            if t_node.get("type") == "Region" and t_node.get("attributes", {}).get("code") != region_filter:
                valid_region = False
            
            if s_node.get("type") == "ModelCode" and s_node.get("attributes", {}).get("market") != region_filter:
                valid_region = False
            if t_node.get("type") == "ModelCode" and t_node.get("attributes", {}).get("market") != region_filter:
                valid_region = False

        edge_info = {
            **edge,
            "dynamic_weight": w,
            "valid_region": valid_region
        }
        all_evaluated_edges.append(edge_info)

        if valid_region:
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
        valid_reg = edge["valid_region"]

        is_active = (s in active_nodes) and (t in active_nodes) and (w <= weight_threshold) and valid_reg
        edge["is_active"] = is_active
        if is_active:
            active_edges.append(edge)

    return active_nodes, active_edges, all_evaluated_edges


# ==========================================
# 3. BigQuery GQL 및 LLM Context 생성기
# ==========================================
def generate_bigquery_gql(seed_node_id: str, intent: str, max_hop: int, weight_threshold: float, region_filter: str, node_dict: dict) -> tuple:
    """
    발화 의도(INFO_SEARCH vs PURCHASE_INTENT) 및 온톨로지 필터 조건에 따라
    1) BigQuery GQL 표준 쿼리문 (Intent-Driven Semantic Query)
    2) BigQuery GRAPH_TABLE 멀티홉 서브그래프 쿼리문 (GoogleSQL GQL)
    을 정돈된 포맷과 대문자 키워드로 생성합니다.
    """
    seed_node = node_dict.get(seed_node_id, {})
    seed_name = seed_node.get("name", "소렌토")
    seed_type = seed_node.get("type", "FamilyCar")

    region_filter_gql = f"\n  AND (target.market = '{region_filter}' OR target.code = '{region_filter}')" if region_filter != "ALL" else ""
    region_clause_gtable = f"\n        AND (target:Region.code = '{region_filter}' OR EXISTS {{ (target)-[:AVAILABLE_IN]->(:Region {{code: '{region_filter}'}}) }})" if region_filter != "ALL" else ""

    if intent == "INFO_SEARCH":
        gql_standard = f"""-- =========================================================================
-- Google Cloud BigQuery GQL: 정보 탐색 의도 (INFO_SEARCH)
-- 핵심 목적: 신차 출시 일정 및 마케팅 소구점(HAS_KSP) 우선 추출
-- =========================================================================
GRAPH `gcp-project-auto-kg.vehicle_ontology.auto_semantic_graph`
MATCH (f:{seed_type} {{name: '{seed_name}'}})-[e:HAS_KSP]->(m:MarketingInfo)
WHERE e.weight <= {weight_threshold:.2f}{region_filter_gql}
RETURN 
    f.name AS family_name,
    m.name AS ksp_title,
    m.desc AS marketing_details,
    e.weight AS relevance_cost
ORDER BY 
    relevance_cost ASC;"""
    else:
        gql_standard = f"""-- =========================================================================
-- Google Cloud BigQuery GQL: 실구매 상담 의도 (PURCHASE_INTENT)
-- 핵심 목적: 모델 트림별 파워트레인 및 사양/옵션(APPLIES_SPEC) 정밀 추출
-- =========================================================================
GRAPH `gcp-project-auto-kg.vehicle_ontology.auto_semantic_graph`
MATCH (f:{seed_type} {{name: '{seed_name}'}})<-[:BELONGS_TO]-(m:ModelCode)-[e:APPLIES_SPEC]->(s:SpecItem)
WHERE e.weight <= {weight_threshold:.2f}{region_filter_gql}
RETURN 
    f.name AS family_name,
    m.name AS model_variant,
    s.name AS specification_item,
    s.desc AS spec_details,
    e.weight AS option_priority_cost
ORDER BY 
    option_priority_cost ASC;"""

    gql_graph_table = f"""-- =========================================================================
-- Google Cloud BigQuery GoogleSQL GQL (GRAPH_TABLE) Dynamic Subgraph Query
-- Max Hop: {max_hop} | Weight Threshold: <= {weight_threshold:.2f} | Region Filter: {region_filter}
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
    `gcp-project-auto-kg.vehicle_ontology.auto_semantic_graph`,
    MATCH (start:{seed_type} {{id: '{seed_node_id}'}})
          -[e:BELONGS_TO|AVAILABLE_IN|HAS_KSP|APPLIES_SPEC*1..{max_hop}]-(target)
    WHERE e.weight <= {weight_threshold:.2f}{region_clause_gtable}
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


def build_llm_context_and_response(intent: str, seed_node_id: str, active_nodes: dict, active_edges: list, node_dict: dict, user_query: str):
    """
    활성화된 온톨로지 서브그래프를 LLM Context로 구조화하고 Mock 답변을 생성합니다.
    """
    seed_node = node_dict.get(seed_node_id, {})
    
    extracted_specs = []
    extracted_ksp = []
    extracted_models = []

    for nid, meta in active_nodes.items():
        if nid == seed_node_id:
            continue
        n = node_dict.get(nid, {})
        ntype = n.get("type")
        nname = n.get("name")
        ndesc = n.get("desc")
        nattr = n.get("attributes", {})

        if ntype == "SpecItem":
            extracted_specs.append(f"• **{nname}**: {ndesc} ({json.dumps(nattr, ensure_ascii=False)})")
        elif ntype == "MarketingInfo":
            extracted_ksp.append(f"• **{nname}**: {ndesc}")
        elif ntype == "ModelCode":
            extracted_models.append(f"• **{nname}** ({nattr.get('powertrain', '')})")

    context_payload = {
        "user_query": user_query,
        "inferred_intent": intent,
        "seed_entity": {
            "id": seed_node.get("id"),
            "name": seed_node.get("name"),
            "type": seed_node.get("type"),
            "desc": seed_node.get("desc")
        },
        "ontology_filtered_knowledge": {
            "active_models": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == "ModelCode"],
            "marketing_ksp_items": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == "MarketingInfo"],
            "specification_items": [node_dict[nid]["name"] for nid in active_nodes if node_dict.get(nid, {}).get("type") == "SpecItem"],
            "total_active_entities": len(active_nodes),
            "total_active_relations": len(active_edges)
        }
    }

    if intent == "INFO_SEARCH":
        if "소렌토" in seed_node.get("name", ""):
            llm_text = f"""### 📢 [소렌토 마케팅 & 신형 정보 안내]
고객님께서 문의하신 **소렌토** 관련 최신 정보입니다:

1. **2025 신형 출시 & 사전계약 프로모션**:
   - 2025년형 모델의 사전계약이 진행 중이며, 연 2.9% 저금리 혜택과 50만원 상당의 얼리버드 전용 바우처가 제공됩니다.
2. **시그니처 디자인 & 첨단 편의 사양**:
   - 기아의 최신 '스타맵 시그니처 라이팅'과 '12.3인치 파노라믹 커브드 디스플레이'가 적용되어 한층 세련된 인테리어를 자랑합니다.
3. **패밀리 SUV 최적화 공간성**:
   - 2,815mm의 동급 최장 휠베이스로 3열 탑승 및 시트 폴딩 시 최대 2,044L의 광활한 차박/적재 공간을 제공합니다.
4. **친환경 하이브리드 세제 혜택**:
   - 1.6T 터보 하이브리드 모델(복합연비 15.7km/L) 선택 시 취득세 및 개별소비세 최대 143만원 감면 혜택이 적용됩니다."""
        else:
            llm_text = f"""### 📢 [싼타페 마케팅 & 신차 정보 안내]
고객님께서 문의하신 **싼타페** 관련 주요 마케팅 및 디자인 하이라이트입니다:

1. **H-라이트 시그니처 & 테라스 콘셉트 테일게이트**:
   - 현대차 엠블럼을 형상화한 H-라이트와 야외 아웃도어 활동에 특화된 대형 테라스 테일게이트가 적용되었습니다.
2. **압도적인 실내 공간**:
   - 패밀리 캠핑 및 차박에 최적화된 동급 최고 수준의 3열 헤드룸과 대용량 트렁크 공간을 제공합니다.
3. **하이브리드 친환경 혜택**:
   - 1.6T HEV 기준 복합 15.7km/L 연비 달성 및 공영주차장 50% 감면 등 친환경차 혜택을 누릴 수 있습니다."""
    else:
        if "소렌토" in seed_node.get("name", ""):
            llm_text = f"""### 🛒 [소렌토 구매 가이드 & 최적 사양 추천]
고객님의 구매 의도에 맞춰 지식 그래프 온톨로지 기반으로 필터링된 최적 사양/옵션 조합을 추천드립니다:

1. **추천 트림 및 파워트레인**:
   - **MQ4 HEV (1.6T 터보 하이브리드)**: 도심 주행 연비(15.7km/L)와 부드러운 승차감, 취득세 감면 혜택으로 가장 선호도가 높습니다.
   - 고속 주행 및 견인력이 필요한 경우 **2.5T 가솔린 터보(281마력)**를 추천합니다.
2. **필수 추천 옵션 조합**:
   - **드라이브 와이즈 (ADAS)**: 고속도로 주행 보조 2(HDA2) 및 스마트 크루즈 컨트롤로 패밀리 장거리 운행 필수.
   - **HUD (헤드업 디스플레이)**: 주행 중 전방 시야 분산 없이 내비게이션/ADAS 정보 확인.
   - **빌트인 캠 2 (QHD)**: 전후방 고화질 녹화 및 음성 녹음, 증강현실 뷰 지원.
   - **전자식 AWD**: 눈길/빗길 안전 주행 및 터레인 모드 지원."""
        else:
            llm_text = f"""### 🛒 [싼타페 구매 가이드 & 트림/옵션 추천]
고객님의 실구매 및 견적 검토를 위한 **디 올 뉴 싼타페** 사양 분석입니다:

1. **파워트레인 선택 가이드**:
   - **1.6T 하이브리드 (MX5 HEV)**: 최고출력 245ps 시스템 출력과 우수한 경제성 제공.
   - **2.5T 가솔린 터보 (MX5)**: 넉넉한 281마력 출력 및 HTRAC 4륜구동 조화.
2. **주요 추천 사양**:
   - **드라이브 와이즈 / 스마트센스**: 안전 하차 보조 및 차로 변경 지원.
   - **HUD & 빌트인 캠 2**: 시인성 높은 헤드업 디스플레이와 깔끔한 순정형 블랙박스.
   - **듀얼 파노라마 선루프**: 쾌적한 실내 개방감 제공."""

    return context_payload, llm_text, extracted_specs, extracted_ksp, extracted_models


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
def render_pyvis_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict) -> str:
    """
    선택된 IDE 테마 팔레트가 완벽하게 적용된 PyVis 물리 엔진(ForceAtlas2) HTML을 생성합니다.
    (Light/Dark 테마에 따른 배경 및 노드 라벨 스트로크 자동 동기화)
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    node_colors = theme["node_colors"]

    net = Network(height="680px", width="100%", bgcolor=graph_bg, font_color=text_color, directed=True, cdn_resources="remote")

    # 1. 노드 추가
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
                size = 28 if ntype in ["FamilyCar", "ModelCode"] else 22
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

    # 2. 엣지 추가
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
            if rel == "HAS_KSP":
                edge_color = node_colors.get("MarketingInfo", "#C084FC")
            elif rel == "APPLIES_SPEC":
                edge_color = node_colors.get("SpecItem", "#4ADE80")
            elif rel == "BELONGS_TO":
                edge_color = node_colors.get("FamilyCar", "#60A5FA")
            else:
                edge_color = node_colors.get("Region", "#22D3EE")

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

    # 3. 물리 엔진 파라미터
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

    # 4. Tooltip CSS 인젝션 (테마 일치)
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
def render_cytoscape_network(nodes, all_evaluated_edges, active_nodes: dict, seed_node_id: str, node_dict: dict, theme: dict) -> str:
    """
    선택된 IDE 테마 팔레트가 완벽하게 적용된 Cytoscape.js COSE 레이아웃 그래프 HTML을 생성합니다.
    """
    is_dark = theme.get("is_dark", True)
    graph_bg = theme.get("graph_bg", theme["bg"])
    card_bg = theme["card_bg"]
    border_color = theme["border"]
    text_color = theme["text"]
    node_colors = theme["node_colors"]

    elements = []

    # Cytoscape 노드 데이터 구성
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
                "size": 56 if is_seed else (44 if ntype in ["FamilyCar", "ModelCode"] and is_active else (36 if is_active else 24)),
                "opacity": 1.0 if is_active else 0.3,
                "tooltip": node_tooltip
            }
        })

    # Cytoscape 엣지 데이터 구성
    for idx, edge in enumerate(all_evaluated_edges):
        s = edge["source"]
        t = edge["target"]
        rel = edge["relation"]
        w = edge["dynamic_weight"]
        is_active = edge.get("is_active", False)

        s_name = node_dict.get(s, {}).get("name", s)
        t_name = node_dict.get(t, {}).get("name", t)
        edge_tooltip = create_edge_plain_tooltip(edge, is_active, s_name, t_name)

        if rel == "HAS_KSP":
            edge_color = node_colors.get("MarketingInfo", "#C084FC")
        elif rel == "APPLIES_SPEC":
            edge_color = node_colors.get("SpecItem", "#4ADE80")
        elif rel == "BELONGS_TO":
            edge_color = node_colors.get("FamilyCar", "#60A5FA")
        else:
            edge_color = node_colors.get("Region", "#22D3EE")

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


# ==========================================
# 7. Main Streamlit Application
# ==========================================
def main():
    nodes, edges = generate_graph_data()
    node_dict = {n["id"]: n for n in nodes}

    # -------------------------------------------------------------
    # A. 좌측 사이드바 상단: 🎨 10대 IDE 테마 선택 (Light 4종 + Dark 6종)
    # -------------------------------------------------------------
    st.sidebar.markdown("## 🎨 UI Theme & Ontology")
    selected_theme_name = st.sidebar.selectbox(
        "🎨 IDE UI 테마 선택",
        list(THEMES.keys()),
        index=0,
        help="개발자 인기 Light 4종 / Dark 6종 IDE 테마로 전체 UI 배경 및 노드/엣지 배색을 실시간 전환합니다."
    )
    active_theme = THEMES[selected_theme_name]

    # 선택된 테마에 맞춰 전체 Streamlit 스타일 동적 주입
    st.markdown(generate_theme_css(active_theme), unsafe_allow_html=True)

    mode_label = "🌙 다크 모드" if active_theme.get("is_dark", True) else "☀️ 라이트 모드"
    st.sidebar.caption(f"현재 테마: **{selected_theme_name}** ({mode_label})")
    st.sidebar.markdown("---")

    # -------------------------------------------------------------
    # B. 발화 시뮬레이션 및 온톨로지 의도 제어
    # -------------------------------------------------------------
    st.sidebar.markdown("### 🗣️ 1. 발화 입력 및 프리셋")
    
    preset_options = [
        "Preset 1: '신형 소렌토 곧 나온다며?' (마케팅/출시 정보)",
        "Preset 2: '소렌토 구매하려고 하는데 옵션 추천해줘' (실구매/사양)",
        "Preset 3: '싼타페 하이브리드 신차 소식 알려줘' (마케팅/출시 정보)",
        "Preset 4: '싼타페 풀옵션 사양 및 견적 확인' (실구매/사양)",
        "직접 입력 (Custom Utterance)"
    ]
    selected_preset = st.sidebar.radio("발화 시나리오 선택", preset_options, index=0)

    if selected_preset.startswith("Preset 1"):
        default_query = "신형 소렌토 곧 나온다며?"
        default_intent_idx = 0  # INFO_SEARCH
        default_seed = "FC_SORENTO"
    elif selected_preset.startswith("Preset 2"):
        default_query = "소렌토 구매하려고 하는데 옵션 추천해줘"
        default_intent_idx = 1  # PURCHASE_INTENT
        default_seed = "FC_SORENTO"
    elif selected_preset.startswith("Preset 3"):
        default_query = "싼타페 하이브리드 신차 소식 알려줘"
        default_intent_idx = 0  # INFO_SEARCH
        default_seed = "FC_SANTAFE"
    elif selected_preset.startswith("Preset 4"):
        default_query = "싼타페 풀옵션 사양 및 견적 확인"
        default_intent_idx = 1  # PURCHASE_INTENT
        default_seed = "FC_SANTAFE"
    else:
        default_query = "소렌토 하이브리드 사양과 최신 혜택 알려줘"
        default_intent_idx = 0
        default_seed = "FC_SORENTO"

    user_query = st.sidebar.text_input("사용자 발화 (Utterance)", value=default_query)

    st.sidebar.markdown("### 🎯 2. 발화 의도(Intent) & 탐색 시작 노드")
    intent_options = ["INFO_SEARCH", "PURCHASE_INTENT"]
    intent = st.sidebar.radio(
        "추론된 의도 (Inferred Intent)",
        intent_options,
        index=default_intent_idx,
        help="• INFO_SEARCH: HAS_KSP 가중치 0.1(최우선), APPLIES_SPEC 0.9(탐색제외)\n• PURCHASE_INTENT: APPLIES_SPEC 가중치 0.1(최우선), HAS_KSP 0.9(탐색제외)"
    )

    if intent == "INFO_SEARCH":
        st.sidebar.markdown(f"""
        <div style='background:{active_theme["card_bg"]}; border-left:4px solid {active_theme["node_colors"]["MarketingInfo"]}; padding:8px; border-radius:4px; font-size:12px; color:{active_theme["text"]};'>
            <b>[가중치 규칙: 정보 탐색 (INFO_SEARCH)]</b><br/>
            • <code>HAS_KSP</code>: <b>0.1 (최우선 활성)</b><br/>
            • <code>APPLIES_SPEC</code>: <b>0.9 (임계값 초과 시 차단)</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div style='background:{active_theme["card_bg"]}; border-left:4px solid {active_theme["node_colors"]["SpecItem"]}; padding:8px; border-radius:4px; font-size:12px; color:{active_theme["text"]};'>
            <b>[가중치 규칙: 실구매 의도 (PURCHASE_INTENT)]</b><br/>
            • <code>APPLIES_SPEC</code>: <b>0.1 (최우선 활성)</b><br/>
            • <code>HAS_KSP</code>: <b>0.9 (임계값 초과 시 차단)</b>
        </div>
        """, unsafe_allow_html=True)

    car_node_candidates = [n["id"] for n in nodes if n["type"] in ["FamilyCar", "ModelCode"]]
    seed_idx = car_node_candidates.index(default_seed) if default_seed in car_node_candidates else 0
    seed_node_id = st.sidebar.selectbox(
        "탐색 시작 노드 (Seed Node)",
        car_node_candidates,
        index=seed_idx,
        format_func=lambda x: f"[{node_dict[x]['type']}] {node_dict[x]['name']}"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ 3. 온톨로지 탐색 파라미터")
    
    max_hop = st.sidebar.slider("Max Hop (탐색 깊이)", min_value=1, max_value=3, value=2, step=1)
    weight_threshold = st.sidebar.slider(
        "Edge Weight Threshold (임계값)",
        min_value=0.0,
        max_value=1.0,
        value=0.50,
        step=0.05,
        help="가중치가 이 임계값 이하인 엣지만 서브그래프 탐색 경로로 활성화됩니다."
    )

    # 사이드바 가중치 임계값 설명 가이드 박스
    st.sidebar.markdown(f"""
    <div class='weight-guide-box'>
        <b>💡 Edge Weight(가중치) 임계값의 의미:</b><br/>
        1. <b>비용 기반 가중치(Cost-based):</b> 가중치가 <b>0에 가까울수록</b> 현재 의도와의 연관도(우선순위)가 높습니다.<br/>
        2. <b>임계값 ({weight_threshold:.2f} 이하만 통과):</b><br/>
        • <b>임계값을 낮출 때 (0.1~0.3):</b> 핵심 정보(의도 직결 KSP 또는 필수 사양)만 엄격하게 필터링<br/>
        • <b>임계값을 높일 때 (0.6~1.0):</b> 연관도가 낮은 주변 노드까지 탐색 범위를 넓혀 컨텍스트 확장
    </div>
    """, unsafe_allow_html=True)

    region_filter = st.sidebar.selectbox(
        "지역 필터 (Region Constraint)",
        ["KR", "US", "ALL"],
        index=0,
        help="[Axiom] 선택된 Region에 귀속된 ModelCode 및 유효 사양/마케팅 관계만 활성화합니다."
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
        region_filter=region_filter
    )

    # -------------------------------------------------------------
    # D. 메인 헤더 & KPI 메트릭 바
    # -------------------------------------------------------------
    st.markdown(f"## 🚘 Google Cloud BigQuery Graph Semantic Subgraph Explorer")
    st.markdown(
        f"현재 발화 의도 **`{intent}`** 및 시작 노드 **`{node_dict[seed_node_id]['name']}`** 기반으로 실시간 온톨로지 공리 탐색이 완료되었습니다. (테마: **`{selected_theme_name}`**)"
    )

    # 메인 화면 가중치 원리 안내 카드
    st.markdown(f"""
    <div class='main-guide-card'>
        <div style='font-weight:700; color:{active_theme["accent"]}; font-size:0.95rem; margin-bottom:6px;'>
            🧠 온톨로지 동적 가중치 탐색 원리 (Intent-Driven Dynamic Traversal)
        </div>
        <div style='display:flex; flex-wrap:wrap; gap:16px;'>
            <div style='flex:1; min-width:280px;'>
                <b>1. 비용 기반 가중치 (Cost-based Weight):</b><br/>
                온톨로지 그래프에서는 <b>가중치(Weight) 값이 0에 가까울수록</b> 사용자 의도와의 연관도(우선순위)가 높음을 뜻합니다.
                현재 의도(<code>{intent}</code>)에 따라 <b>{'HAS_KSP(마케팅/출시)' if intent == 'INFO_SEARCH' else 'APPLIES_SPEC(사양/옵션)'}</b> 관계는 <b>0.1</b>로 최우선 배정되고, 반대 관계는 <b>0.9</b>로 후순위 처리됩니다.
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
            <div class='metric-value'>{subgraph_coverage}% <span style='font-size:0.9rem; color:{active_theme["node_colors"]["SpecItem"]};'>Filtered</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    # 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드 Expander
    with st.expander("💡 온톨로지 관계(Edge) 정의 및 비즈니스 역할 가이드", expanded=False):
        st.markdown("""
        #### 📌 엣지(Edge) 관계별 비즈니스 레이어 구분
        
        | 구분 | `HAS_KSP` (마케팅 & 세일즈 관점) | `APPLIES_SPEC` (실구매 & 기술 스펙 관점) |
        |---|---|---|
        | **핵심 질문** | **"왜 이 차를 사야 하는가?"** (Why to Buy) | **"이 차에 실제로 무엇이 들어있는가?"** (What is Inside) |
        | **출발 노드** | `FamilyCar` (상위 차종 단위 / 예: 소렌토, 싼타페) | `ModelCode` (상세 트림·파워트레인 단위 / 예: MQ4 HEV) |
        | **도착 노드** | `MarketingInfo` (마케팅 소구점·USP) | `SpecItem` (하드웨어/옵션 사양) |
        | **데이터 성격** | • 신차/페이스리프트 출시 일정<br>• 구매 혜택 및 프로모션 바우처<br>• 주력 USP (공간성, 스타맵 라이팅, 패밀리 브랜딩) | • 파워트레인 제원 (1.6T HEV 245ps, 2.5T 가솔린)<br>• 전자식 AWD (터레인 모드), HUD, 빌트인 캠 2<br>• 트림별 기본/선택 품목 패키지 (드라이브 와이즈) |
        | **적합한 의도** | **정보 탐색 (`INFO_SEARCH`)** | **실구매 상담 (`PURCHASE_INTENT`)** |
        
        ---
        
        #### 🎯 발화 의도(Intent)에 따른 가변 컨텍스트 제어 및 LLM 연계 원리
        - **정보 탐색 의도 (`INFO_SEARCH`):**
          - 신차 정보나 마케팅 혜택을 알고 싶은 초기 탐색 고객에게는 복잡한 부품 사양을 숨기고, `HAS_KSP` 엣지의 가중치를 **0.1 (최우선)**로 낮춰 핵심 소구점을 LLM 주입 컨텍스트로 신속하게 전달합니다.
        - **실구매 상담 의도 (`PURCHASE_INTENT`):**
          - 실제 견적과 옵션을 비교하는 실구매 고객에게는 모호한 마케팅 문구를 배제하고, `APPLIES_SPEC` 엣지의 가중치를 **0.1 (최우선)**로 낮춰 정확한 파워트레인 및 옵션 데이터만 LLM 주입 컨텍스트로 정밀 전달합니다.
        """)

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # E. 메인 패널 수직 배치 (Full Width Vertical Layout)
    # -------------------------------------------------------------
    
    # =============================================================
    # 1. [상단 영역] Interactive Knowledge Graph Visualization (Full Width)
    # =============================================================
    st.markdown("### 🕸️ Interactive Knowledge Graph Visualization")

    # 듀얼 렌더링 엔진 선택기 (PyVis vs Cytoscape.js)
    col_rend1, col_rend2 = st.columns([1.3, 2.7])
    with col_rend1:
        renderer_options = [
            "1. PyVis (Vis.js 물리 시뮬레이션)",
            "2. Cytoscape.js (엔지니어링/구조적 레이아웃)"
        ]
        selected_renderer = st.selectbox(
            "📊 그래프 렌더링 엔진 선택",
            renderer_options,
            index=0,
            help="동일한 온톨로지 서브그래프 데이터를 PyVis(물리) 및 Cytoscape.js(구조적)로 전환하여 비교합니다."
        )
    with col_rend2:
        if "PyVis" in selected_renderer:
            st.info("⚡ **PyVis (Vis.js Physics)**: ForceAtlas2 기반 물리 시뮬레이션으로 노드가 넓게 퍼지며 자유로운 드래그와 유기적 줌을 제공합니다.")
        else:
            st.info("📐 **Cytoscape.js (COSE Layout)**: 생물정보학 및 네트워크 공학 표준 그래프 엔진으로 안정적인 구조적 위상과 베지어 곡선 엣지를 제공합니다.")

    st.markdown("""
    <div class='legend-box'>
        <span class='badge badge-node-family'>● FamilyCar</span>
        <span class='badge badge-node-model'>● ModelCode</span>
        <span class='badge badge-node-spec'>● SpecItem</span>
        <span class='badge badge-node-marketing'>● MarketingInfo</span>
        <span class='badge badge-node-region'>● Region</span>
        <span style='font-size:0.75rem; opacity:0.85; margin-left:auto;'>★ 노란 테두리: 시작 노드 | 반투명: 비활성 노드</span>
    </div>
    """, unsafe_allow_html=True)

    # 선택된 렌더러에 따라 분기 렌더링 (현재 테마 팔레트 주입)
    if "PyVis" in selected_renderer:
        graph_html = render_pyvis_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme)
        components.html(graph_html, height=710, scrolling=False)
        st.caption("💡 PyVis 팁: 마우스 휠로 줌인/줌아웃하고, 노드를 드래그하여 자유롭게 배치할 수 있습니다. 마우스 호버 시 카드형 툴팁이 표시됩니다.")
    else:
        cytoscape_html = render_cytoscape_network(nodes, all_evaluated_edges, active_nodes, seed_node_id, node_dict, active_theme)
        components.html(cytoscape_html, height=710, scrolling=False)
        st.caption("💡 Cytoscape.js 팁: 배경을 드래그하여 팬(Pan) 이동하고, 노드/엣지 위에 마우스를 올리면 상세 카드 툴팁이 나타납니다.")

    st.markdown(f"<div style='margin-top: 24px; margin-bottom: 24px;'><hr style='border:0; border-top:1px solid {active_theme['border']};'/></div>", unsafe_allow_html=True)

    # =============================================================
    # 2. [하단 영역] Dynamic Cypher/GQL Query & Grounding Result (Full Width)
    # =============================================================
    st.markdown("### ⚡ Dynamic Cypher/GQL Query & Grounding Result")

    tab1, tab2, tab3 = st.tabs([
        "📝 BigQuery GQL Query",
        "🤖 LLM Grounding Context & Output",
        "📊 Filtered Subgraph Tables"
    ])

    with tab1:
        gql_standard, gql_graph_table = generate_bigquery_gql(seed_node_id, intent, max_hop, weight_threshold, region_filter, node_dict)

        st.markdown("#### 1. BigQuery GQL 표준 쿼리 (Intent-Driven Semantic Query)")
        st.code(gql_standard, language="sql")

        st.markdown("#### 2. BigQuery `GRAPH_TABLE` 멀티홉 탐색 쿼리 (Dynamic Multi-Hop GoogleSQL)")
        st.code(gql_graph_table, language="sql")

        with st.expander("🔍 openCypher 호환 표준 쿼리 보기"):
            cypher_query = f"""// openCypher Standard Query
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

    with tab2:
        context_payload, llm_response, specs, ksps, models = build_llm_context_and_response(
            intent=intent,
            seed_node_id=seed_node_id,
            active_nodes=active_nodes,
            active_edges=active_edges,
            node_dict=node_dict,
            user_query=user_query
        )

        st.markdown("#### 💬 LLM Response Simulation (RAG 기반 응답)")
        st.info(llm_response)

        st.markdown("#### 📦 LLM 주입 컨텍스트 (Injected Grounding Prompt Context)")
        st.json(context_payload)

    with tab3:
        st.markdown("#### 1. 활성화된 노드 목록 (Active Nodes)")
        node_table_rows = []
        for nid, meta in active_nodes.items():
            n = node_dict.get(nid, {})
            node_table_rows.append({
                "Node ID": nid,
                "Name": n.get("name"),
                "Type": n.get("type"),
                "Hop Distance": meta.get("hop"),
                "Traverse Cost": meta.get("cost"),
                "Relevance Score": meta.get("relevance")
            })
        df_nodes = pd.DataFrame(node_table_rows).sort_values(by=["Hop Distance", "Traverse Cost"])
        st.dataframe(df_nodes, hide_index=True)

        st.markdown("#### 2. 활성화된 엣지 목록 (Active Edges)")
        edge_table_rows = []
        for e in active_edges:
            edge_table_rows.append({
                "Source Node": node_dict.get(e["source"], {}).get("name", e["source"]),
                "Target Node": node_dict.get(e["target"], {}).get("name", e["target"]),
                "Relation": e["relation"],
                "Weight": e["dynamic_weight"],
                "Description": e.get("desc", "")
            })
        df_edges = pd.DataFrame(edge_table_rows)
        st.dataframe(df_edges, hide_index=True)


if __name__ == "__main__":
    main()
