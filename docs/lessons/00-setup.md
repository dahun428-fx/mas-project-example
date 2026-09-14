# 0교시 · 환경 준비

날짜: 2026-09-10 · Step 0 · 상태: 완료

## 한 것
- 빈 GitHub 리포 클론, 문서·설정 골격 커밋 (`README.md`, `.gitignore`, `.env.example`, `requirements.txt`, `pytest.ini`, `pyproject.toml`, `docs/`).
- `python3.12 -m venv .venv`, `pip install -r requirements.txt`.
- LLM 은 OpenAI 만 쓰기로 결정. 기본 모델 `gpt-5.4-nano`.

## 겪은 문제
- 실제 API 키를 `.env.example`(git 추적 파일)에 넣었음 → `.env`(gitignore) 로 옮기고 예시 파일은 비움. **규칙: 키는 .env 에만.**

## 다음 교시
- 1교시: OpenAI 호출 1회로 답 받는 CLI.
