import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta


TICKERS = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "DXY": "DX-Y.NYB",       # 달러인덱스
    "Gold": "GC=F",           # 금 선물
    "Oil": "CL=F",            # WTI 원유
    "US10Y": "^TNX",          # 미국 10년 국채금리
}


def get_stock_data(period: str = "3mo") -> dict:
    """yfinance로 주요 자산 데이터 수집"""
    result = {}
    for name, ticker in TICKERS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period=period)
            if not hist.empty:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else current
                change_pct = ((current - prev) / prev) * 100
                week_ago = hist["Close"].iloc[-5] if len(hist) >= 5 else hist["Close"].iloc[0]
                month_ago = hist["Close"].iloc[-20] if len(hist) >= 20 else hist["Close"].iloc[0]
                result[name] = {
                    "ticker": ticker,
                    "current": round(current, 2),
                    "change_pct": round(change_pct, 2),
                    "week_change_pct": round(((current - week_ago) / week_ago) * 100, 2),
                    "month_change_pct": round(((current - month_ago) / month_ago) * 100, 2),
                    "high_52w": round(hist["Close"].max(), 2),
                    "low_52w": round(hist["Close"].min(), 2),
                    "history": hist["Close"],
                    "ohlcv": hist[["Open", "High", "Low", "Close"]],
                }
        except Exception as e:
            result[name] = {"error": str(e)}
    return result


def get_bitcoin_data() -> dict:
    """CoinGecko API로 비트코인 데이터 수집"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()["market_data"]

        return {
            "current": data["current_price"]["usd"],
            "change_pct_24h": round(data["price_change_percentage_24h"], 2),
            "change_pct_7d": round(data["price_change_percentage_7d"], 2),
            "change_pct_30d": round(data["price_change_percentage_30d"], 2),
            "market_cap": data["market_cap"]["usd"],
            "volume_24h": data["total_volume"]["usd"],
            "high_24h": data["high_24h"]["usd"],
            "low_24h": data["low_24h"]["usd"],
            "ath": data["ath"]["usd"],
            "ath_change_pct": round(data["ath_change_percentage"]["usd"], 2),
        }
    except Exception as e:
        return {"error": str(e)}


def get_bitcoin_history(days: int = 90) -> pd.Series:
    """CoinGecko API로 비트코인 가격 이력 수집"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "daily"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        prices = resp.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("date")["price"]
        return df
    except Exception:
        return pd.Series(dtype=float)


def get_fear_greed_index() -> dict:
    """공포탐욕지수 수집 (alternative.me)"""
    try:
        resp = requests.get("https://api.alternative.me/fng/?limit=7", timeout=10)
        resp.raise_for_status()
        data = resp.json()["data"]
        latest = data[0]
        return {
            "value": int(latest["value"]),
            "classification": latest["value_classification"],
            "history": [{"value": int(d["value"]), "classification": d["value_classification"]} for d in data],
        }
    except Exception as e:
        return {"error": str(e)}


def build_market_summary(stock_data: dict, btc_data: dict, fear_greed: dict) -> str:
    """Gemini에게 전달할 시장 데이터 요약 텍스트 생성"""
    lines = ["=== 현재 시장 데이터 ===\n"]

    lines.append("[주요 자산 현황]")
    for name, d in stock_data.items():
        if "error" not in d:
            lines.append(
                f"- {name}: {d['current']:,.2f} "
                f"(일간 {d['change_pct']:+.2f}%, "
                f"주간 {d['week_change_pct']:+.2f}%, "
                f"월간 {d['month_change_pct']:+.2f}%)"
            )

    if "error" not in btc_data:
        lines.append(
            f"\n[비트코인 (BTC/USD)]"
            f"\n- 현재가: ${btc_data['current']:,.0f}"
            f"\n- 24h: {btc_data['change_pct_24h']:+.2f}%"
            f"\n- 7일: {btc_data['change_pct_7d']:+.2f}%"
            f"\n- 30일: {btc_data['change_pct_30d']:+.2f}%"
            f"\n- 시가총액: ${btc_data['market_cap']:,.0f}"
            f"\n- ATH 대비: {btc_data['ath_change_pct']:+.2f}%"
        )

    if "error" not in fear_greed:
        lines.append(
            f"\n[암호화폐 공포탐욕지수]"
            f"\n- 현재: {fear_greed['value']} ({fear_greed['classification']})"
        )

    return "\n".join(lines)
