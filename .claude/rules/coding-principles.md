# Coding Principles — egov-demo

> 전자정부표준프레임워크 + Karpathy 가이드라인
>
> **이 프로젝트는 Java + Spring + MyBatis + JSP + Oracle 11g 기반이다.**
> **DB는 Oracle 11g 단일 DBMS만 사용한다.**

---

## 4원칙 (Andrej Karpathy Guidelines)

### 1. 코딩하기 전에 먼저 생각하기

구현 전에 불명확한 점을 명시적으로 드러낸다.

**해야 할 일:**
```text
"조회 기능을 추가해줘" → 다음을 확인합니다.

1. 조회 범위: 모든 데이터인가? 특정 조건인가?
2. 페이징: 필요한가? 페이지 크기는?
3. 필드: 어떤 컬럼을 조회할까?
4. 화면: 목록 조회만? 상세조회도?
5. 정렬: 어떤 컬럼으로 정렬할까?

추가 정보가 필요합니다.
```

**하지 말 것:**
```text
가정하고 바로 구현 → SQL + Controller + JSP 한 번에 작성
```

### 2. 단순함을 먼저 선택하기

필요해지기 전에 복잡도를 추가하지 않는다.

**Good:**
```java
// 요청한 것만 구현
public List<SampleVO> selectList(SampleVO searchVO) {
    return sampleDAO.selectList(searchVO);
}
```

**Bad:**
```java
// 미요청 기능을 미리 추가
@Cacheable(value = "samples")
@Async
public CompletableFuture<List<SampleVO>> selectListWithCache(...) {
    // 200줄의 복잡한 캐싱·비동기 로직
}
```

**규칙:**
- 요청하지 않은 공통 유틸 클래스 자의적 생성 금지
- VO에 미사용 필드 미리 추가 금지
- 보기에 좋은 코드가 아니라 기능이 필요한 코드만

### 3. 외과수술처럼 변경하기

기존 코드를 수정할 때는 정해진 범위만 변경한다.

**Good:**
```diff
  public void selectList(SampleVO vo) {
      // 기존 주석 유지
-     String keyword = vo.getKeyword();  // null 체크 없음
+     String keyword = vo.getKeyword();
+     if (keyword == null) keyword = "";  // null 처리 추가만
      
      return sampleDAO.selectList(vo);  // 기존 코드 유지
  }
```

**Bad:**
```diff
  public void selectList(SampleVO vo) {
+     /**
+      * 샘플 목록을 조회한다.
+      */
-     String keyword = vo.getKeyword();
+     String keyword = Optional.ofNullable(vo.getKeyword()).orElse("");
+     String[] keywords = keyword.split(" ");
+     // 정렬 순서 변경
-     return sampleDAO.selectList(vo);
+     vo.setOrderBy("DESC");  // 추가 로직
+     List<SampleVO> result = sampleDAO.selectListWithCache(vo);
+     return applyComplexFilter(result);
  }
```

**규칙:**
- 작동 중인 코드 임의 리팩토링 금지
- 요청하지 않은 주석·포맷 개선 금지
- 버그 수정 범위만 변경

### 4. 목표 중심으로 실행하기

성공 기준을 먼저 정의하고 검증 가능한 단계로 나눈다.

**Good:**
```text
목표: 사용자 조회 기능 추가

1단계: JUnit 테스트 작성 (음수 케이스 포함)
       - 검색 없을 때 전체 목록
       - 검색어 있을 때 필터링
       - 페이징 정상 동작
   검증: mvn test → 테스트 실패 (Red)

2단계: Controller + Service + DAO + SQL 구현
   검증: mvn test → 모든 테스트 통과 (Green)

3단계: 기존 테스트 통과 확인
   검증: mvn test → 회귀 없음

4단계: 최종 검증
   검증:
   - mvn -q -DskipTests compile → PASS
   - mvn -q test → PASS
   - mvn -q -DskipTests package → PASS
```

**Bad:**
```text
목표: 사용자 조회 기능 추가

[구체적인 단계 없이]
여러 파일을 한 번에 수정하고 테스트만 실행
→ 어디서 문제가 나는지 파악 어려움
```

---

## 계층 분리 원칙

각 계층은 정해진 역할만 수행한다.

| 계층 | 역할 | 금지 |
|------|------|------|
| **Controller** | 파라미터 바인딩, 검증, Service 호출, View 반환 | SQL, DAO 직접 호출, 비즈니스 로직 |
| **Service** | 업무 규칙, 트랜잭션, DAO 조합 | SQL 직접 작성, HTTP 처리 |
| **DAO** | MyBatis Mapper 호출만 | 비즈니스 if문, 세션/인증 |
| **VO** | 데이터 운반 (ComDefaultVO 상속) | 로직 포함 금지 |

**Code Example:**

```java
// ❌ 금지: Controller에서 DAO 직접 호출
@RestController
public class SampleController {
    @Autowired
    private SampleDAO sampleDAO;  // 직접 호출
    
    @GetMapping("/list")
    public List<SampleVO> list() {
        return sampleDAO.selectList(...);  // Service 우회
    }
}

// ✅ 올바른 방식
@RestController
public class SampleController {
    @Autowired
    private EgovSampleService sampleService;
    
    @GetMapping("/list")
    public List<SampleVO> list() {
        return sampleService.selectList(...);  // Service 경유
    }
}
```

---

## 명명 규칙 (eGov 표준)

```
Controller  : EgovSampleController
Service     : EgovSampleService
ServiceImpl  : EgovSampleServiceImpl
DAO         : SampleDAO
VO          : SampleVO (페이징 있으면 SampleDefaultVO)
메서드      : selectList, selectDetail, insertSample
URL         : /example/sample/selectList.do
JSP View    : EgovSampleList.jsp, EgovSampleDetail.jsp
```

**전체 eGov 네이밍:**
- 패키지: `egovframework.example.<domain>`
- 테이블: `SAMPLE_TBL` (Oracle 대문자)
- 컬럼: `SAMPLE_NM`, `SAMPLE_ID` (Oracle 대문자)
- Sequence: `SEQ_SAMPLE_ID`

---

## Database: Oracle 11g 전용

**이 프로젝트는 Oracle 11g만 사용한다.**

### 허용

```sql
-- ROWNUM 페이징 (3중 SELECT)
SELECT * FROM (
    SELECT ROWNUM RN, A.* FROM (
        SELECT COL1, COL2 FROM TABLE_NM
        ORDER BY REG_DT DESC
    ) A WHERE ROWNUM <= 100
) WHERE RN > 0

-- Sequence
SEQ_SAMPLE.NEXTVAL

-- Oracle 함수
SYSDATE, NVL(), DECODE(), TO_CHAR(), TO_DATE()
```

### 금지

```sql
-- 금지: Oracle 12c+
OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY

-- 금지: MySQL
LIMIT 10 OFFSET 10
AUTO_INCREMENT

-- 금지: PostgreSQL
OFFSET ... LIMIT

-- 금지: 파라미터 직접 치환 (SQL Injection)
WHERE NAME = '${searchKeyword}'

-- 금지: SELECT *
SELECT * FROM TABLE_NM
```

---

## 완료 기준

세 가지 모두 통과:

```bash
mvn -q -DskipTests compile  # PASS
mvn -q test                  # PASS (실패 0건)
mvn -q -DskipTests package   # PASS
```

---

## 체크리스트

- [ ] 계층 분리 준수 (Controller → Service → DAO)
- [ ] VO는 ComDefaultVO 상속 (페이징 있는 경우)
- [ ] 모든 URL은 `.do` 패턴
- [ ] SQL은 Oracle 11g 호환만
- [ ] ROWNUM 페이징 3중 구조 사용
- [ ] 파라미터 바인딩 `#{}` 사용
- [ ] 테스트 케이스 작성 (정상·예외)
- [ ] 콘솔 로그 없음
