---
name: db-decision-records
description: 공공데이터베이스 설계결정 기록(ADR) 스킬. 표준용어 선택, 도메인 매핑, 기관표준 신규생성 사유, 정규화 수준, 대상 DBMS 선택 등 데이터 설계 결정을 구조화된 ADR로 남긴다. 트리거 - "설계 결정 기록", "ADR", "왜 이렇게 설계", "결정 근거".
allowed-tools: Read, Write, Grep, Glob
---

# db-decision-records (공공DB 설계결정 ADR)

> ECC `architecture-decision-records` 스킬의 ADR 포맷·라이프사이클을 **공공데이터베이스 설계 결정**에 적용하도록 현지화한다.
> 포맷 원본: [`../architecture-decision-records/SKILL.md`](../architecture-decision-records/SKILL.md) 를 필요 시 참조한다.

## 사용 시점

- da-agent 5단계(변경관리)에서 설계 결정을 기록할 때
- 표준/도메인/정규화/DBMS 선택 등 대안 중 하나를 택했을 때
- "왜 이 표준용어/도메인/구조인가"를 질문받을 때(기존 ADR 조회)

## 기록 대상 결정 (공공DB)

- **표준 선택**: 공공표준 적용 vs 기관(KOMSA)표준 신규생성 사유
- **도메인 매핑**: 동일 형식단어에 복수 도메인 후보가 있을 때의 선택 근거
- **정규화 수준**: 반정규화 허용 여부와 사유(성능·이력관리 등)
- **식별자 설계**: 자연키 vs 인조키, 주식별자 선정
- **대상 DBMS**: Oracle vs PostgreSQL 선택 및 그에 따른 설계 영향
- **개인정보 처리**: 암호화 도메인 적용·분리 저장 결정

## ADR 포맷

```markdown
# ADR-NNNN: [결정 제목]

## 상태
제안 / 채택 / 폐기 / 대체(ADR-XXXX)

## 맥락
- 요구사항번호, 대상 엔터티/컬럼, DBMS
- 결정이 필요한 이유

## 결정
- 무엇을 어떻게 하기로 했는가

## 검토한 대안
### 대안 1
- 내용 / 장단점 / 기각 사유

## 결과
- 긍정 / 부정 / 위험
- 메타데이터·산출물·마이그레이션에 미치는 영향
```

## 저장 위치 및 인덱스

- 디렉토리: `docs/04. db-deliverables/{요구사항번호}/adr/ADR-NNNN-{제목}.md`
- 인덱스: 같은 폴더 `ADR-index.md`에 번호·제목·상태·날짜를 1행씩 누적

## 경계

- 결정의 표준 적합성 판정은 metadata-agent 결과를 근거로 인용한다(자체 판정 금지).
- 코드/데이터를 수정하지 않는다(결정 기록만).
