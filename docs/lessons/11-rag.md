# 11교시 · RAG (지식 문서 검색과 근거 인용)

날짜: 2026-09-23 · Step 7 · 상태: 구현 완료, 테스트·평가 스크립트 작성 중

## 목표
`KnowledgeAgent` 가 LLM 내부 지식이 아니라 **우리 문서**를 근거로 답하게 한다. 출처를 댈 수 있고, 회사가 정한 기준값을 쓸 수 있다.

## 흐름
```
[준비, 문서 바뀔 때만]  knowledge.jsonl → embed(제목+본문) → knowledge_index.json
[질문마다]             질문 → embed → 문서마다 cosine → threshold 컷 → 상위 3건 → [참고 자료] 블록 → LLM
```

## 만든 파일
- `data/knowledge.jsonl`: 문서 10건(K01~K10). 검사 기준값 5건 + 생활습관 3건 + 검진 안내 2건. 짧게 쓴 이유는 검색 단위(청킹) 때문.
- `mini_mas/rag.py`: `embed`(OpenAI `text-embedding-3-small`, `dimensions=256`), `cosine`(순수 파이썬), `load_docs`, `build_index`, `Retriever(index_path, embed_fn, index).search(query, k=3, threshold=0.35)`, CLI(`build` / 검색).
- `mini_mas/prompts/knowledge.yaml`: `{context}` 슬롯 추가. "[참고 자료]가 있으면 우선 사용, 없으면 일반 범위에서만 설명하고 수치 단정 금지".
- `mini_mas/agents/knowledge.py`: `build_reference_block(hits)`, `retriever` 지연 생성(`@property`), `AgentResult.docs` 채움, metadata `used_rag`.
- `mini_mas/ask.py`: `--raw` 에 근거 문서 출력.
- `.gitignore`: `data/knowledge_index.json` (생성물).

## 핵심 개념
- **임베딩은 글을 좌표로 바꾼다.** 숫자 하나하나에는 의미가 없고, 두 배열 사이의 거리에만 의미가 있다.
- `dimensions=256` 으로 기본 1536 에서 줄였다. 문서 10건 규모에서 정확도 차이는 거의 없고 파일·계산이 6배 가볍다.
- **제목 + 본문을 함께 임베딩**한다. 제목의 핵심 단어가 검색 정확도를 올린다. (원본은 제목 전용 인덱스를 따로 두고 점수를 합침)
- **문턱값 미만은 버리고, 억지로 k개를 채우지 않는다.** 관련 문서가 없으면 빈 목록. 엉뚱한 근거가 붙으면 LLM 이 그걸 인용해 답을 만든다.
- **원본 문서와 인덱스를 분리**한다. 문서를 고치면 `build` 를 다시 돌려야 한다. 인덱스는 생성물이라 커밋하지 않는다.
  (원본 프로젝트는 인덱스를 커밋하고 원본 문서를 커밋하지 않아 재빌드가 불가능한 상태 — 문서집 Doc 18)
- `embed_fn` / `index` 주입으로 API·파일 없이 테스트한다. 에이전트에 `llm` 을 주입한 것과 같은 패턴.
- 10교시와 반대 정책: 검진 데이터는 **없다는 사실을 명시**해야 하고(없는 연도가 곧 답), 지식 문서는 **없으면 블록을 통째로 뺀다**(자료 없이도 답할 수 있다).
- 질문마다 임베딩 API 가 1회 추가된다. 그래서 개인 데이터 컨텍스트가 있는 `NumbersAgent` 는 RAG 를 쓰지 않는다.
- 문서 수만 건이 되면 전수 cosine 은 느려져 FAISS 같은 전용 라이브러리로 간다. 지금 단계에서 라이브러리를 쓰면 내부가 안 보인다.

## 겪은 문제
- `knowledge.jsonl` 10번째 줄이 붙여넣기 중 잘림(`"te의, 이상, ...`) → `JSONDecodeError: Expecting ':' delimiter: line 1 column 123`.
  오류의 "line 1" 은 **파일 줄 번호가 아니라** `json.loads` 에 넘긴 그 한 줄 기준. 줄 단위로 돌며 실패한 줄 번호를 찍는 검증 코드로 위치를 찾았다.
- JSONL 은 한 글자만 어긋나도 그 줄 전체가 깨진다. 대신 나머지 줄은 멀쩡하고 끝에 추가만 하면 되어 대량 데이터에 쓴다. 로드 시 줄 단위 검증을 붙여 두는 게 관례.

## 남은 확인
```bash
python -m pytest              # tests/unit/test_rag.py 작성 후 66 passed
python -m eval.rag_eval       # 수락 기준 top-3 적중률 ≥ 90% (12문항)
python -m mini_mas.ask "LDL 기준이 뭐야?" --raw
```

## 다음 교시
- 12교시 (Step 9): 관측성과 비용. 모든 LLM 호출을 turn 단위로 SQLite 에 기록하고, 턴당 비용·지연·호출 수를 집계한다.
