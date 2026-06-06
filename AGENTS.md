# AGENTS.md — Codex 작업 표준

> Codex CLI가 이 프로젝트에서 수행하는 역할과 금지사항을 정의한다.
> Claude Code가 승인한 작업계획 범위 안에서 **Java + Spring + MyBatis + JSP + Oracle 11g 코드를 구현**한다.

---

## 역할

```
Claude (PM · 품질 게이트)
  ├── 요구사항 승인
  ├── 영향 범위 분석
  ├── 작업계획 작성
  ├── 코드 리뷰
  └── 완료 승인
        ↓ 작업계획 전달
Gemini (요구사항 상세화)
  └── 기능 명세 · 수용조건 작성
        ↓ 명세 승인 후
Codex (코드 구현)
  └── Java / SQL / JSP / 테스트 코드 작성
```

---

## 구현 대상

| 레이어 | 파일 | 명명 규칙 |
|------|------|---------|
| Controller | `EgovXxxController.java` | `Egov` prefix 필수 |
| Service 인터페이스 | `EgovXxxService.java` | `Egov` prefix 필수 |
| Service 구현체 | `EgovXxxServiceImpl.java` | `Impl` suffix 필수 |
| DAO | `XxxDAO.java` | DAO suffix |
| VO | `XxxVO.java` | ComDefaultVO 상속 (페이징 있는 경우) |
| Mapper XML | `XxxMapper.xml` | sqlmap 경로 |
| JSP View | `EgovXxxList.jsp` | Egov prefix |

---

## 패키지 구조

```
src/main/java/egovframework/example/<domain>/
├── service/
│   ├── EgovXxxService.java
│   ├── XxxVO.java
│   └── XxxDefaultVO.java (선택)
├── serviceImpl/
│   └── EgovXxxServiceImpl.java
└── web/
    └── EgovXxxController.java

src/main/resources/egovframework/sqlmap/example/<domain>/
└── XxxMapper.xml

src/main/webapp/WEB-INF/jsp/egov/<domain>/
├── EgovXxxList.jsp
├── EgovXxxRegist.jsp
└── EgovXxxDetail.jsp
```

---

## Oracle 11g 전용 SQL 규칙 (절대 준수)

### 허용

```xml
<!-- ROWNUM 기반 3중 페이징 (변경 불가) -->
SELECT * FROM (
    SELECT ROWNUM RN, A.* FROM (
        SELECT COL1, COL2 FROM TABLE_NM
        WHERE 1=1
        <if test="searchKeyword != null and searchKeyword != ''">
            AND COLUMN_NM LIKE '%' || #{searchKeyword} || '%'
        </if>
        ORDER BY FRST_REGIST_PNTTM DESC
    ) A WHERE ROWNUM <![CDATA[<=]]> #{lastIndex}
) WHERE RN <![CDATA[>]]> #{firstIndex}

<!-- Sequence 자동증가 -->
SEQ_XXX.NEXTVAL

<!-- Oracle 함수 -->
SYSDATE, NVL(), DECODE(), TO_CHAR(), TO_DATE()
```

### 금지

```sql
-- 금지: Oracle 12c 이상 문법
OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY

-- 금지: MySQL/PostgreSQL
LIMIT 10 OFFSET 10

-- 금지: 사용자 입력값 직접 치환
WHERE NAME = '${searchKeyword}'   -- SQL Injection 위험

-- 금지: SELECT *
SELECT * FROM TABLE_NM   -- (ROWNUM 래핑 제외)
```

---

## 금지 행동 (절대 준수)

- `${}`를 ORDER BY 화이트리스트 검증 없이 사용
- Controller에서 DAO 직접 호출
- 승인되지 않은 URL 패턴 변경 (`.do` 유지)
- Oracle 11g 외 DBMS 문법 사용
- 요청하지 않은 공통 유틸 클래스 자의적 생성
- 미사용 VO 필드 추가
- 로직 있는 VO 작성

---

## 완료 보고 형식

```
✅ mvn -q -DskipTests compile  → PASS
✅ mvn -q test                  → PASS (실패 0건)
✅ mvn -q -DskipTests package   → PASS

변경 파일:
- src/main/java/egovframework/example/sample/web/EgovSampleController.java
- src/main/java/egovframework/example/sample/service/EgovSampleService.java
- src/main/java/egovframework/example/sample/serviceImpl/EgovSampleServiceImpl.java
- src/main/java/egovframework/example/sample/service/SampleVO.java
- src/main/resources/egovframework/sqlmap/example/sample/SampleMapper.xml
- src/main/webapp/WEB-INF/jsp/egov/sample/EgovSampleList.jsp

Oracle 11g 호환성: 확인됨
남은 이슈: 없음
```
