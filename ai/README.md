# AI (3단계)

3단계(AI 예측 모델 개발) 기준 구현 내용입니다.

- 학습 데이터 분할 (`train/validation/test`)
- 베이스라인 모델 (이동평균 룰 기반)
- 머신러닝 모델 학습 (Simple Logistic Regression)
- 평가 지표 (Sharpe Ratio, MDD, 승률, Accuracy)
- 모델 파일 버전 저장 (`ai/models/artifacts`)
- 매수/매도/관망 신호 생성 (`ai/signals/generated`)

## 실행 방법

### 1) 2단계 데이터 준비

`backend/data/market_data.db`에 `market_features`가 있어야 합니다.

### 2) 학습 실행

```powershell
python -m ai.models.run_training --db-path backend/data/market_data.db --symbol AAPL --market US
```

### 3) 테스트 실행

```powershell
python -m pytest ai/tests/test_training_pipeline.py -q
```
