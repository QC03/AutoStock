# Git 브랜치 전략

AutoStock은 아래 Git Flow 경량 전략을 사용합니다.

## 브랜치 종류

- `main`: 운영 기준 안정 브랜치
- `develop`: 통합 개발 브랜치
- `feature/*`: 기능 단위 작업 브랜치

## 작업 규칙

1. 새 기능 작업은 `develop`에서 `feature/*` 브랜치 생성
2. 기능 완료 후 PR을 `develop`으로 생성
3. 릴리즈 시 `develop`을 `main`으로 머지
4. 긴급 수정은 `main`에서 `hotfix/*` 생성 후 `main`, `develop` 모두 반영

## 브랜치 네이밍 예시

- `feature/data-ingestion`
- `feature/backend-auth`
- `feature/frontend-dashboard`
- `hotfix/order-timeout`

## 커밋/PR 권장

- 작은 단위 커밋
- PR 템플릿에 변경 요약, 테스트 방법, 체크리스트 포함
- 최소 1회 코드 리뷰 후 머지
