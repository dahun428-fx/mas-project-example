# mas-project-example

건강 AI코치 MAS(`llm-aicoach-007-MAS`)를 교재로 삼아, 미니 멀티에이전트 시스템 `mini_mas`를 처음부터 쌓아 올리는 학습 프로젝트.
커리큘럼 원문: 문서집 Doc 20 (6주 12단계). 진행 상황은 `docs/progress.md`.

## 규칙

- **읽기보다 만들기.** 원본을 먼저 읽되, 구현은 스스로 한 뒤 원본과 diff 한다.
- 단계마다 `docs/worksheets/stepNN.md` 에 **수락 기준**이 적혀 있다. 테스트도 학습자가 쓴다.
- 단계 끝에 `docs/diff-notes/stepNN.md` 에 "내 구현 vs 원본" 차이 3가지와 원본이 그렇게 한 이유를 적는다.

## 시작

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # 키 채우기
pytest                         # 아직 테스트가 없으면 "no tests ran" 이 정상
```

## 역할 분담

- **학습자**: 모든 코드(구현·테스트·CLI)를 직접 작성한다.
- **지도교사(Claude)**: 단계별 과제 명세와 인터페이스 계약을 산문으로 주고, 작성된 코드를 리뷰하고, 막히면 힌트를 준다. 코드를 대신 쓰지 않는다.
