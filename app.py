import os
import sys
import streamlit as st
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

st.markdown("""
<style>
.metric-card {
    background: #1e1e2e;
    border-radius: 10px;
    padding: 16px;
    margin: 4px 0;
}
.positive { color: #00d084; }
.negative { color: #ff4b4b; }
.neutral  { color: #a0aec0; }
</style>
""", unsafe_allow_html=True)


# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ 설정")

    api_key = os.getenv("GEMINI_API_KEY", "") or st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
    else:
        st.success("Gemini API 키 로드됨 ✓")

    st.divider()
    period_map = {"1개월": "1mo", "3개월": "3mo", "6개월": "6mo", "1년": "1y"}
    selected_period_label = st.selectbox("데이터 기간", list(period_map.keys()), index=1)
    selected_period = period_map[selected_period_label]

    st.divider()
    st.markdown("### 자산 선택 (예측)")
    predict_assets = st.multiselect(
        "예측할 자산",
        ["비트코인 (BTC)", "S&P500", "NASDAQ", "KOSPI", "KOSDAQ"],
        default=["비트코인 (BTC)", "S&P500", "KOSPI"],
    )
    predict_period = st.selectbox("예측 기간", ["1주일", "2주일", "1개월", "3개월"], index=2)

    st.divider()
    refresh_btn = st.button("🔄 데이터 새로고침", use_container_width=True)


# ── 데이터 로드 (캐시) ───────────────────────────────────────
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


# ── 헤더 ─────────────────────────────────────────────────────
st.title("📊 경제 분석 & 자산 가격 예측 시스템")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 데이터 기간: {selected_period_label}")
st.divider()


# ── 탭 구성 ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 시장 현황",
    "🤖 AI 종합 분석",
    "🎯 가격 예측",
    "💬 AI 질의응답",
])


# ══════════════════════════════════════════════════════════════
# TAB 1: 시장 현황
# ══════════════════════════════════════════════════════════════
with tab1:
    # 비트코인 별도 표시
    st.subheader("₿ 비트코인 (BTC/USD)")
    if "error" not in btc_data:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("현재가", f"${btc_data['current']:,.0f}",
                    f"{btc_data['change_pct_24h']:+.2f}% (24h)")
        col2.metric("7일 변동", f"{btc_data['change_pct_7d']:+.2f}%")
        col3.metric("30일 변동", f"{btc_data['change_pct_30d']:+.2f}%")
        col4.metric("24h 고가", f"${btc_data['high_24h']:,.0f}")
        col5.metric("ATH 대비", f"{btc_data['ath_change_pct']:+.2f}%",
                    f"ATH ${btc_data['ath']:,.0f}")
    else:
        st.warning(f"BTC 데이터 로드 실패: {btc_data['error']}")

    # 공포탐욕지수
    if "error" not in fear_greed:
        fg_val = fear_greed["value"]
        fg_class = fear_greed["classification"]
        color = "#ff4b4b" if fg_val < 25 else "#ff9900" if fg_val < 45 else "#a0aec0" if fg_val < 55 else "#00d084"
        st.markdown(
            f"**공포탐욕지수:** <span style='color:{color}; font-size:1.1em'>"
            f"{fg_val} ({fg_class})</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # 주식 / 지수
    st.subheader("🌍 글로벌 주요 지수")
    stock_names = ["S&P500", "NASDAQ", "KOSPI", "KOSDAQ"]
    cols = st.columns(4)
    for i, name in enumerate(stock_names):
        d = stock_data.get(name, {})
        if "error" not in d:
            delta_color = "normal"
            cols[i].metric(
                label=name,
                value=f"{d['current']:,.2f}",
                delta=f"{d['change_pct']:+.2f}% (일간)",
            )
        else:
            cols[i].warning(f"{name} 로드 실패")

    st.divider()

    # 매크로 지표
    st.subheader("🌐 매크로 지표")
    macro_names = ["US10Y", "DXY", "Gold", "Oil"]
    cols2 = st.columns(4)
    for i, name in enumerate(macro_names):
        d = stock_data.get(name, {})
        if "error" not in d:
            cols2[i].metric(
                label=name,
                value=f"{d['current']:,.2f}",
                delta=f"{d['change_pct']:+.2f}% (일간)",
            )

    st.divider()

    # 차트 섹션
    st.subheader("📉 가격 차트")
    chart_col1, chart_col2 = st.columns(2)

    # BTC 차트
    with chart_col1:
        if not btc_history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=btc_history.index,
                y=btc_history.values,
                mode="lines",
                name="BTC/USD",
                line=dict(color="#F7931A", width=2),
                fill="tozeroy",
                fillcolor="rgba(247,147,26,0.1)",
            ))
            fig.update_layout(
                title="Bitcoin (BTC/USD) - 90일",
                xaxis_title="",
                yaxis_title="USD",
                template="plotly_dark",
                height=300,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig, use_container_width=True)

    # KOSPI 차트
    with chart_col2:
        kospi = stock_data.get("KOSPI", {})
        if "history" in kospi:
            hist = kospi["history"]
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=hist.index,
                y=hist.values,
                mode="lines",
                name="KOSPI",
                line=dict(color="#3182ce", width=2),
                fill="tozeroy",
                fillcolor="rgba(49,130,206,0.1)",
            ))
            fig2.update_layout(
                title=f"KOSPI - {selected_period_label}",
                xaxis_title="",
                yaxis_title="포인트",
                template="plotly_dark",
                height=300,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # S&P500 + NASDAQ 비교 차트
    sp = stock_data.get("S&P500", {})
    nq = stock_data.get("NASDAQ", {})
    if "history" in sp and "history" in nq:
        fig3 = go.Figure()
        # 정규화 (100 기준)
        sp_norm = (sp["history"] / sp["history"].iloc[0]) * 100
        nq_norm = (nq["history"] / nq["history"].iloc[0]) * 100
        fig3.add_trace(go.Scatter(x=sp_norm.index, y=sp_norm.values,
                                  mode="lines", name="S&P500", line=dict(color="#48BB78")))
        fig3.add_trace(go.Scatter(x=nq_norm.index, y=nq_norm.values,
                                  mode="lines", name="NASDAQ", line=dict(color="#9F7AEA")))
        fig3.update_layout(
            title=f"S&P500 vs NASDAQ 상대 성과 (기준=100) - {selected_period_label}",
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# TAB 2: AI 종합 분석
# ══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🤖 Gemini AI 종합 시장 분석")
    st.caption("현재 시장 데이터를 기반으로 Gemini AI가 종합 분석을 제공합니다.")

    if not api_key:
        st.warning("사이드바에 Gemini API 키를 입력하세요.")
    else:
        if st.button("🔍 AI 분석 시작", type="primary", key="analyze_btn"):
            with st.spinner("Gemini AI 분석 중..."):
                try:
                    analyzer = GeminiAnalyzer(api_key)
                    result = analyzer.analyze_market(market_summary)
                    st.session_state["analysis_result"] = result
                except Exception as e:
                    st.error(f"분석 실패: {e}")

        if "analysis_result" in st.session_state:
            st.markdown(st.session_state["analysis_result"])

    with st.expander("📋 현재 시장 데이터 원문 보기"):
        st.text(market_summary)


# ══════════════════════════════════════════════════════════════
# TAB 3: 가격 예측
# ══════════════════════════════════════════════════════════════
with tab3:
    st.subheader(f"🎯 {predict_period} 가격 예측")
    st.caption(f"선택된 자산: {', '.join(predict_assets)}")

    if not api_key:
        st.warning("사이드바에 Gemini API 키를 입력하세요.")
    elif not predict_assets:
        st.warning("사이드바에서 예측할 자산을 선택하세요.")
    else:
        if st.button("🚀 가격 예측 시작", type="primary", key="predict_btn"):
            analyzer = GeminiAnalyzer(api_key)
            for asset in predict_assets:
                with st.spinner(f"{asset} 예측 중..."):
                    try:
                        result = analyzer.predict_price(asset, market_summary, predict_period)
                        st.session_state[f"predict_{asset}"] = result
                    except Exception as e:
                        st.session_state[f"predict_{asset}"] = f"예측 실패: {e}"

        for asset in predict_assets:
            key = f"predict_{asset}"
            if key in st.session_state:
                with st.expander(f"📌 {asset} 예측 결과", expanded=True):
                    st.markdown(st.session_state[key])


# ══════════════════════════════════════════════════════════════
# TAB 4: AI 질의응답
# ══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("💬 AI 질의응답")
    st.caption("현재 시장 데이터를 기반으로 자유롭게 질문하세요.")

    if not api_key:
        st.warning("사이드바에 Gemini API 키를 입력하세요.")
    else:
        # 빠른 질문 버튼
        st.markdown("**빠른 질문:**")
        quick_cols = st.columns(3)
        quick_questions = [
            "지금 비트코인 매수 타이밍인가요?",
            "KOSPI 전망이 어떻게 되나요?",
            "달러 강세가 자산에 미치는 영향은?",
        ]
        for i, q in enumerate(quick_questions):
            if quick_cols[i].button(q, key=f"quick_{i}"):
                st.session_state["chat_input"] = q

        user_question = st.text_area(
            "질문 입력",
            value=st.session_state.get("chat_input", ""),
            placeholder="예: 현재 금리 상황에서 어떤 자산에 투자하는 게 좋을까요?",
            height=100,
        )

        if st.button("📨 질문하기", type="primary", key="ask_btn") and user_question.strip():
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
                except Exception as e:
                    st.error(f"오류: {e}")

        # 대화 이력 표시
        if "qa_history" in st.session_state:
            for item in reversed(st.session_state["qa_history"]):
                with st.chat_message("user"):
                    st.write(f"[{item['time']}] {item['q']}")
                with st.chat_message("assistant"):
                    st.markdown(item["a"])


# ── 푸터 ─────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ 이 시스템은 참고용 정보를 제공하며, 투자 결정의 최종 책임은 사용자에게 있습니다.")
