import google.generativeai as genai
from datetime import datetime


SYSTEM_PROMPT = """당신은 글로벌 금융 시장 전문 분석가입니다.
실시간 시장 데이터와 거시경제 지표를 바탕으로 객관적이고 전문적인 분석을 제공합니다.

분석 시 다음 요소를 반드시 고려하세요:
- 미국 연준(Fed) 금리 정책 방향
- 지정학적 리스크 (중동, 무역전쟁 등)
- 기술적 분석 지표 (추세, 지지/저항선)
- 기관 투자자 동향
- 시장 심리 (공포탐욕지수)
- 달러 인덱스 및 금리 상관관계

한국어로 명확하고 구체적으로 답변하며, 투자 결정은 사용자 책임임을 항상 명시하세요."""


class GeminiAnalyzer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )

    def analyze_market(self, market_summary: str) -> str:
        """전체 시장 종합 분석"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        prompt = f"""
{today} 기준 시장 데이터를 분석해주세요.

{market_summary}

다음 항목으로 구분하여 분석해주세요:

## 1. 시장 전반 분석
- 현재 시장 국면 (강세/약세/횡보) 판단
- 주요 상관관계 분석 (달러, 금리, 원유 영향)

## 2. 미국 증시 (S&P500 / NASDAQ)
- 현황 및 단기 방향성
- 주요 지지/저항 레벨

## 3. 한국 증시 (KOSPI / KOSDAQ)
- 현황 및 단기 방향성
- 글로벌 시장과의 연동성

## 4. 비트코인 (BTC)
- 현황 및 시장 심리
- 매크로 환경과의 연관성

## 5. 핵심 리스크 요인
- 단기 (1-2주) 주요 변수
- 중기 (1-3개월) 주요 변수

※ 이 분석은 참고용이며 투자 결정의 최종 책임은 투자자에게 있습니다.
"""
        response = self.model.generate_content(prompt)
        return response.text

    def predict_price(self, asset: str, market_summary: str, period: str = "1개월") -> str:
        """특정 자산 가격 예측"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        prompt = f"""
{today} 기준으로 {asset}의 {period} 후 가격을 예측해주세요.

{market_summary}

다음 형식으로 분석해주세요:

## {asset} {period} 가격 예측

### 기술적 분석
- 현재 추세
- 주요 지지선 / 저항선

### 시나리오별 예측
| 시나리오 | 확률 | 예상 가격 범위 | 조건 |
|---------|------|--------------|------|
| 강세 | XX% | ... | ... |
| 기본 | XX% | ... | ... |
| 약세 | XX% | ... | ... |

### 주요 변수
- 상승 촉매
- 하락 리스크

### 투자 전략 제안
- 진입 시점
- 손절 / 목표가 기준

※ 이 예측은 참고용이며 실제 투자 결정의 책임은 투자자에게 있습니다.
"""
        response = self.model.generate_content(prompt)
        return response.text

    def ask_custom(self, question: str, market_summary: str) -> str:
        """사용자 질문에 답변"""
        prompt = f"""
현재 시장 데이터:
{market_summary}

사용자 질문: {question}

위 시장 데이터를 참고하여 전문적으로 답변해주세요.
"""
        response = self.model.generate_content(prompt)
        return response.text
