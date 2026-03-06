import os
import sys
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from data.fetcher import (
    get_stock_data,
    get_bitcoin_data,
    get_bitcoin_history,
    get_fear_greed_index,
    build_market_summary,
)
from analysis.gemini_analyzer import GeminiAnalyzer

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="경제 분석 & 자산 가격 예측",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 글로벌 CSS ────────────────────────────────────────────────
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1117 50%, #0a0e1a 100%);
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid rgba(48, 54, 61, 0.8);
}

/* 헤더 배너 */
.hero-banner {
    background: linear-gradient(135deg, #1a1f35 0%, #0f1729 40%, #1a1035 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 1.9em;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 0.85em;
    color: #64748b;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.4);
    color: #818cf8;
    font-size: 0.72em;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* 메트릭 카드 */
.metric-card {
    background: linear-gradient(145deg, #161b22 0%, #1c2128 100%);
    border: 1px solid rgba(48, 54, 61, 0.9);
    border-radius: 12px;
    padding: 18px 20px;
    margin: 4px 0;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: rgba(99, 102, 241, 0.4);
}
.metric-label {
    font-size: 0.75em;
    color: #6b7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 1.45em;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
    line-height: 1.2;
}
.metric-delta-pos {
    font-size: 0.82em;
    color: #10b981;
    font-weight: 600;
}
.metric-delta-neg {
    font-size: 0.82em;
    color: #ef4444;
    font-weight: 600;
}
.metric-delta-neu {
    font-size: 0.82em;
    color: #6b7280;
    font-weight: 600;
}

/* 섹션 헤더 */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(48, 54, 61, 0.6);
}
.section-title {
    font-size: 1.0em;
    font-weight: 600;
    color: #94a3b8;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.section-icon {
    font-size: 1.1em;
}

/* AI 분석 결과 박스 */
.analysis-box {
    background: linear-gradient(145deg, #0f1729 0%, #161b22 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-left: 3px solid #6366f1;
    border-radius: 12px;
    padding: 24px 28px;
    margin-top: 16px;
}

/* 빠른 질문 버튼 */
.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s;
}

/* 공포탐욕 배지 */
.fg-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 18px;
    border-radius: 24px;
    font-weight: 700;
    font-size: 0.95em;
}

/* 사이드바 섹션 */
.sidebar-section {
    background: rgba(22, 27, 34, 0.6);
    border: 1px solid rgba(48, 54, 61, 0.5);
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
}
.sidebar-section-title {
    font-size: 0.72em;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* expander 스타일 */
[data-testid="stExpander"] {
    border: 1px solid rgba(48, 54, 61, 0.7) !important;
    border-radius: 10px !important;
    background: rgba(22, 27, 34, 0.4) !important;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(22, 27, 34, 0.5);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(48, 54, 61, 0.5);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    color: #6b7280;
}
.stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.15) !important;
    color: #818cf8 !important;
}

/* 경고/성공 메시지 */
.stAlert {
    border-radius: 10px;
}

/* 푸터 */
.footer-text {
    text-align: center;
    color: #374151;
    font-size: 0.78em;
    padding: 8px 0;
}
</style>
""", unsafe_allow_html=True)


# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 4px 0 16px 0;">
        <div style="font-size:1.1em; font-weight:700; color:#e2e8f0;">
            📊 분석 설정
        </div>
        <div style="font-size:0.78em; color:#4b5563; margin-top:3px;">
            데이터 및 예측 옵션
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API 키
    st.markdown('<div class="sidebar-section-title">🔑 API 설정</div>', unsafe_allow_html=True)
    api_key = os.getenv("GEMINI_API_KEY", "") or st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...",
                                label_visibility="collapsed")
        st.caption("Gemini API 키를 입력하면 AI 분석을 사용할 수 있습니다.")
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; gap:8px; background:rgba(16,185,129,0.08);
                    border:1px solid rgba(16,185,129,0.25); border-radius:8px;
                    padding:8px 12px; font-size:0.82em; color:#10b981;">
            ✓ Gemini API 키 로드됨
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 데이터 기간
    st.markdown('<div class="sidebar-section-title">📅 데이터 기간</div>', unsafe_allow_html=True)
    period_map = {"1개월": "1mo", "3개월": "3mo", "6개월": "6mo", "1년": "1y"}
    selected_period_label = st.selectbox(
        "데이터 기간", list(period_map.keys()), index=1, label_visibility="collapsed"
    )
    selected_period = period_map[selected_period_label]

    st.divider()

    # 예측 설정
    st.markdown('<div class="sidebar-section-title">🎯 예측 설정</div>', unsafe_allow_html=True)
    predict_assets = st.multiselect(
        "예측할 자산",
        ["비트코인 (BTC)", "S&P500", "NASDAQ", "KOSPI", "KOSDAQ"],
        default=["비트코인 (BTC)", "S&P500", "KOSPI"],
    )
    predict_period = st.selectbox("예측 기간", ["1주일", "2주일", "1개월", "3개월"], index=2)

    st.divider()

    refresh_btn = st.button("🔄 데이터 새로고침", use_container_width=True, type="secondary")

    st.markdown("""
    <div style="margin-top:20px; padding:10px; border-radius:8px;
                background:rgba(22,27,34,0.5); font-size:0.72em; color:#4b5563; text-align:center;">
        데이터는 5분 캐시 적용<br>새로고침으로 최신 데이터 로드
    </div>
    """, unsafe_allow_html=True)


# ── 데이터 로드 ───────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_all_data(period: str):
    stock_data = get_stock_data(period)
    btc_data = get_bitcoin_data()
    btc_history = get_bitcoin_history(90 if period in ["1mo", "3mo"] else 180)
    fear_greed = get_fear_greed_index()
    return stock_data, btc_data, btc_history, fear_greed


if refresh_btn:
    st.cache_data.clear()

with st.spinner("시장 데이터 수집 중..."):
    stock_data, btc_data, btc_history, fear_greed = load_all_data(selected_period)

market_summary = build_market_summary(stock_data, btc_data, fear_greed)


# ── 헤더 배너 ─────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">Live Market Intelligence</div>
    <div class="hero-title">경제 분석 & 자산 가격 예측 시스템</div>
    <div class="hero-subtitle">
        마지막 업데이트: {now_str} &nbsp;·&nbsp; 데이터 기간: {selected_period_label} &nbsp;·&nbsp;
        Powered by Gemini AI
    </div>
</div>
""", unsafe_allow_html=True)


# ── 헬퍼: 메트릭 카드 렌더링 ─────────────────────────────────
def metric_card(label: str, value: str, delta: str = "", delta_val: float = 0.0):
    if delta:
        if delta_val > 0:
            delta_html = f'<div class="metric-delta-pos">▲ {delta}</div>'
        elif delta_val < 0:
            delta_html = f'<div class="metric-delta-neg">▼ {delta}</div>'
        else:
            delta_html = f'<div class="metric-delta-neu">— {delta}</div>'
    else:
        delta_html = ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ── 헬퍼: 공포탐욕 게이지 ────────────────────────────────────
def fear_greed_gauge(value: int, classification: str):
    color_stops = [
        [0, "#ef4444"], [0.25, "#f97316"], [0.5, "#eab308"],
        [0.75, "#84cc16"], [1.0, "#10b981"]
    ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"<b>{classification}</b>", "font": {"size": 14, "color": "#94a3b8"}},
        number={"font": {"size": 36, "color": "#e2e8f0"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#4b5563",
                     "tickfont": {"color": "#6b7280", "size": 10}},
            "bar": {"color": "rgba(255,255,255,0.0)", "thickness": 0},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25],  "color": "rgba(239,68,68,0.25)"},
                {"range": [25, 45], "color": "rgba(249,115,22,0.2)"},
                {"range": [45, 55], "color": "rgba(234,179,8,0.2)"},
                {"range": [55, 75], "color": "rgba(132,204,22,0.2)"},
                {"range": [75, 100],"color": "rgba(16,185,129,0.25)"},
            ],
            "threshold": {
                "line": {"color": "#e2e8f0", "width": 3},
                "thickness": 0.85,
                "value": value,
            },
        },
    ))
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0"},
    )
    return fig


# ── 차트 공통 레이아웃 ────────────────────────────────────────
CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,17,23,0.6)",
    margin=dict(l=10, r=10, t=44, b=10),
    font=dict(color="#94a3b8", size=11),
    xaxis=dict(gridcolor="rgba(48,54,61,0.5)", zeroline=False),
    yaxis=dict(gridcolor="rgba(48,54,61,0.5)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(48,54,61,0.5)", borderwidth=1),
)


# ── 탭 구성 ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "  📈 시장 현황  ",
    "  🤖 AI 종합 분석  ",
    "  🎯 가격 예측  ",
    "  💬 AI 질의응답  ",
])


# ══════════════════════════════════════════════════════════════
# TAB 1: 시장 현황
# ══════════════════════════════════════════════════════════════
with tab1:

    # ── BTC + 공포탐욕 ──────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">₿</span><span class="section-title">비트코인 (BTC/USD)</span></div>', unsafe_allow_html=True)

    btc_col, fg_col = st.columns([3, 1])

    with btc_col:
        if "error" not in btc_data:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                metric_card("현재가 (USD)", f"${btc_data['current']:,.0f}",
                            f"{btc_data['change_pct_24h']:+.2f}% 24h", btc_data['change_pct_24h'])
            with c2:
                metric_card("7일 변동", f"{btc_data['change_pct_7d']:+.2f}%",
                            "", btc_data['change_pct_7d'])
            with c3:
                metric_card("30일 변동", f"{btc_data['change_pct_30d']:+.2f}%",
                            "", btc_data['change_pct_30d'])
            with c4:
                metric_card("24h 고가", f"${btc_data['high_24h']:,.0f}")
            with c5:
                metric_card("ATH 대비", f"{btc_data['ath_change_pct']:+.2f}%",
                            f"ATH ${btc_data['ath']:,.0f}", btc_data['ath_change_pct'])
        else:
            st.warning(f"BTC 데이터 로드 실패: {btc_data['error']}")

    with fg_col:
        if "error" not in fear_greed:
            fg_val = fear_greed["value"]
            fg_class = fear_greed["classification"]
            st.plotly_chart(fear_greed_gauge(fg_val, fg_class), use_container_width=True)
        else:
            st.info("공포탐욕지수 로드 실패")

    # ── 글로벌 지수 ─────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🌍</span><span class="section-title">글로벌 주요 지수</span></div>', unsafe_allow_html=True)

    stock_names = ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]
    gcols = st.columns(4)
    for i, name in enumerate(stock_names):
        d = stock_data.get(name, {})
        with gcols[i]:
            if "current" in d:
                metric_card(name, f"{d['current']:,.2f}",
                            f"{d['change_pct']:+.2f}% 일간", d['change_pct'])
            else:
                st.warning(f"{name} 로드 실패")

    # ── 매크로 지표 ─────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">🌐</span><span class="section-title">매크로 지표</span></div>', unsafe_allow_html=True)

    macro_names = ["US10Y", "DXY", "Gold", "Oil"]
    macro_labels = {"US10Y": "미국 10Y 국채", "DXY": "달러 인덱스", "Gold": "금 (USD/oz)", "Oil": "WTI 원유"}
    mcols = st.columns(4)
    for i, name in enumerate(macro_names):
        d = stock_data.get(name, {})
        with mcols[i]:
            if "current" in d:
                metric_card(macro_labels.get(name, name), f"{d['current']:,.2f}",
                            f"{d['change_pct']:+.2f}% 일간", d['change_pct'])

    # ── 차트 ────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span class="section-icon">📉</span><span class="section-title">가격 차트 (TradingView)</span></div>', unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)

    def tradingview_iframe(symbol: str, height: int = 400) -> str:
        from urllib.parse import quote
        encoded = quote(symbol, safe="")
        return f"""
        <iframe
          src="https://www.tradingview.com/widgetembed/?symbol={encoded}&interval=D&theme=dark&style=1&locale=kr&timezone=Asia%2FSeoul&hide_side_toolbar=0&allow_symbol_change=0&withdateranges=1"
          width="100%" height="{height}"
          frameborder="0" allowtransparency="true" scrolling="no"
          style="border-radius:12px;">
        </iframe>
        """

    with chart_col1:
        st.caption("Bitcoin / TetherUS — Binance")
        components.html(tradingview_iframe("BINANCE:BTCUSDT"), height=420)

    with chart_col2:
        st.caption("Ethereum / TetherUS — Binance")
        components.html(tradingview_iframe("BINANCE:ETHUSDT"), height=420)


# ══════════════════════════════════════════════════════════════
# TAB 2: AI 종합 분석
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header"><span class="section-icon">🤖</span><span class="section-title">Gemini AI 종합 시장 분석</span></div>', unsafe_allow_html=True)
    st.caption("현재 시장 데이터를 기반으로 Gemini AI가 거시경제 및 자산 동향을 종합 분석합니다.")

    if not api_key:
        st.warning("사이드바에서 Gemini API 키를 입력하세요.")
    else:
        if st.button("🔍 AI 분석 시작", type="primary", key="analyze_btn", use_container_width=False):
            with st.spinner("Gemini AI 분석 중... 잠시 기다려주세요."):
                try:
                    analyzer = GeminiAnalyzer(api_key)
                    result = analyzer.analyze_market(market_summary)
                    st.session_state["analysis_result"] = result
                except Exception as e:
                    st.error(f"분석 실패: {e}")

        if "analysis_result" in st.session_state:
            st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
            st.markdown(st.session_state["analysis_result"])
            st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📋 현재 시장 데이터 원문 보기", expanded=False):
        st.code(market_summary, language="text")


# ══════════════════════════════════════════════════════════════
# TAB 3: 가격 예측
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'<div class="section-header"><span class="section-icon">🎯</span><span class="section-title">{predict_period} 가격 예측</span></div>', unsafe_allow_html=True)

    if predict_assets:
        asset_tags = " &nbsp;".join([
            f'<span style="background:rgba(99,102,241,0.12); border:1px solid rgba(99,102,241,0.3); '
            f'color:#818cf8; padding:3px 10px; border-radius:20px; font-size:0.8em;">{a}</span>'
            for a in predict_assets
        ])
        st.markdown(f"선택된 자산: {asset_tags}", unsafe_allow_html=True)
    st.markdown("")

    if not api_key:
        st.warning("사이드바에서 Gemini API 키를 입력하세요.")
    elif not predict_assets:
        st.warning("사이드바에서 예측할 자산을 1개 이상 선택하세요.")
    else:
        if st.button("🚀 가격 예측 시작", type="primary", key="predict_btn"):
            analyzer = GeminiAnalyzer(api_key)
            progress = st.progress(0)
            for idx, asset in enumerate(predict_assets):
                with st.spinner(f"{asset} 예측 생성 중..."):
                    try:
                        result = analyzer.predict_price(asset, market_summary, predict_period)
                        st.session_state[f"predict_{asset}"] = result
                    except Exception as e:
                        st.session_state[f"predict_{asset}"] = f"예측 실패: {e}"
                progress.progress((idx + 1) / len(predict_assets))
            progress.empty()

        for asset in predict_assets:
            key = f"predict_{asset}"
            if key in st.session_state:
                with st.expander(f"📌 {asset} 예측 결과", expanded=True):
                    st.markdown(st.session_state[key])


# ══════════════════════════════════════════════════════════════
# TAB 4: AI 질의응답
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header"><span class="section-icon">💬</span><span class="section-title">AI 질의응답</span></div>', unsafe_allow_html=True)
    st.caption("현재 시장 데이터를 기반으로 자유롭게 질문하세요.")

    if not api_key:
        st.warning("사이드바에서 Gemini API 키를 입력하세요.")
    else:
        # 빠른 질문
        st.markdown('<div style="font-size:0.82em; color:#6b7280; margin-bottom:8px; font-weight:500;">빠른 질문</div>', unsafe_allow_html=True)
        quick_questions = [
            "지금 비트코인 매수 타이밍인가요?",
            "KOSPI 전망이 어떻게 되나요?",
            "달러 강세가 자산에 미치는 영향은?",
            "현재 매크로 환경 요약",
            "가장 유망한 자산은?",
        ]
        q_cols = st.columns(len(quick_questions))
        for i, q in enumerate(quick_questions):
            if q_cols[i].button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state["chat_input"] = q

        st.markdown("")
        user_question = st.text_area(
            "질문 입력",
            value=st.session_state.get("chat_input", ""),
            placeholder="예: 현재 금리 상황에서 어떤 자산에 투자하는 게 좋을까요?",
            height=90,
            label_visibility="collapsed",
        )

        ask_col, clear_col = st.columns([5, 1])
        with ask_col:
            ask_btn = st.button("📨 질문하기", type="primary", key="ask_btn", use_container_width=True)
        with clear_col:
            if st.button("🗑️", key="clear_btn", use_container_width=True, help="대화 기록 지우기"):
                st.session_state.pop("qa_history", None)
                st.rerun()

        if ask_btn and user_question.strip():
            with st.spinner("Gemini AI 답변 생성 중..."):
                try:
                    analyzer = GeminiAnalyzer(api_key)
                    answer = analyzer.ask_custom(user_question, market_summary)
                    if "qa_history" not in st.session_state:
                        st.session_state["qa_history"] = []
                    st.session_state["qa_history"].append({
                        "q": user_question,
                        "a": answer,
                        "time": datetime.now().strftime("%H:%M:%S"),
                    })
                    st.session_state["chat_input"] = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"오류: {e}")

        # 대화 이력
        if "qa_history" in st.session_state and st.session_state["qa_history"]:
            st.markdown("")
            st.markdown(f'<div style="font-size:0.78em; color:#4b5563; margin-bottom:6px;">대화 기록 ({len(st.session_state["qa_history"])}건)</div>', unsafe_allow_html=True)
            for item in reversed(st.session_state["qa_history"]):
                with st.chat_message("user"):
                    st.markdown(f'<span style="font-size:0.75em; color:#4b5563;">[{item["time"]}]</span> {item["q"]}', unsafe_allow_html=True)
                with st.chat_message("assistant"):
                    st.markdown(item["a"])


# ── 푸터 ─────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="footer-text">
    ⚠️ 이 시스템은 참고용 정보를 제공하며, 투자 결정의 최종 책임은 사용자에게 있습니다. &nbsp;|&nbsp;
    데이터 출처: CoinGecko, Yahoo Finance, Alternative.me
</div>
""", unsafe_allow_html=True)
