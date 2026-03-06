# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

경제 데이터(미국/한국 거시경제 지표) 기반의 비트코인 및 국내외 주식 가격 예측 자료 조사 및 분석 워크스페이스.

## 현재 구조

- `Plan.md` — 최신 경제 분석 및 자산 가격 예측 보고서 (매 조사 시 업데이트)

## 작업 방식

- 경제 자료 조사 시 `WebSearch`로 미국 경제(금리, 인플레이션, 고용), 한국 경제(코스피, 수출), 자산 가격(BTC, S&P500, NASDAQ)을 병렬 검색
- 조사 결과는 `Plan.md`에 덮어쓰기로 업데이트
- 보고서 형식: 미국 경제 → 한국 경제 → BTC → 미국 주식 → 종합 전망 → 출처 순서 유지
