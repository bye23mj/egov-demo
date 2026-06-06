# Testing Rules — egov-demo

> 전자정부표준프레임워크 Maven + JUnit 5 + Oracle 테스트 표준

---

## 테스트 구조

운영 코드와 동일한 패키지 구조:

```
src/test/java/egovframework/example/sample/
├── web/
│   └── EgovSampleControllerTest.java
├── service/
│   └── EgovSampleServiceTest.java
└── service/impl/
    └── SampleDAOTest.java
```

---

## AAA 패턴 (필수)

모든 테스트는 AAA 패턴을 따른다:

```java
@Test
void selectList_검색어없으면_전체목록을_페이징조회한다() throws Exception {
    // Arrange: 테스트 데이터 준비
    SampleVO searchVO = new SampleVO();
    searchVO.setFirstIndex(0);
    searchVO.setRecordCountPerPage(10);

    // Act: 실제 동작 수행
    Map<String, Object> resultMap = sampleService.selectList(searchVO);

    // Assert: 결과 검증
    assertNotNull(resultMap);
    assertTrue(resultMap.containsKey("resultList"));
    assertTrue(resultMap.containsKey("resultCnt"));
    
    @SuppressWarnings("unchecked")
    List<SampleVO> list = (List<SampleVO>) resultMap.get("resultList");
    assertEquals(10, list.size());
}
```

---

## 메서드명 규칙

```
test_{메서드명}_{조건}_{기대결과}

// 예
test_selectList_검색어없으면_전체목록반환한다
test_selectDetail_존재하는ID_상세정보반환한다
test_insertSample_유효한데이터_성공한다
test_insertSample_필수필드누락_예외발생한다
test_updateSample_중복된키_버그없음을확인한다
```

---

## Controller 테스트

Spring Test를 사용한 MockMvc 기반:

```java
@RunWith(SpringRunner.class)
@SpringBootTest
@AutoConfigureMockMvc
public class EgovSampleControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void selectList_정상요청_상태200반환한다() throws Exception {
        mockMvc.perform(
            get("/example/sample/selectList.do")
                .param("pageIndex", "1")
                .contentType(MediaType.APPLICATION_JSON)
        )
        .andExpect(status().isOk())
        .andExpect(view().name("egov/sample/EgovSampleList"));
    }

    @Test
    void insertSample_필수필드누락_예외발생한다() throws Exception {
        mockMvc.perform(
            post("/example/sample/insertSample.do")
                .contentType(MediaType.APPLICATION_FORM_URLENCODED)
        )
        .andExpect(status().is4xxClientError());
    }
}
```

---

## Service 테스트

```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class EgovSampleServiceTest {

    @Autowired
    private EgovSampleService sampleService;

    @Test
    void selectList_정상동작한다() {
        // Arrange
        SampleVO searchVO = new SampleVO();
        searchVO.setFirstIndex(0);
        searchVO.setRecordCountPerPage(10);

        // Act
        Map<String, Object> resultMap = sampleService.selectList(searchVO);

        // Assert
        assertNotNull(resultMap);
        assertNotNull(resultMap.get("resultList"));
    }

    @Test
    void insertSample_필수필드없으면_예외발생한다() {
        // Arrange
        SampleVO vo = new SampleVO();  // 필수 필드 비움

        // Act & Assert
        assertThrows(RuntimeException.class, () -> {
            sampleService.insertSample(vo);
        });
    }
}
```

---

## DAO 테스트 (Oracle 실DB 필수)

**주의:** DAO 테스트는 **실제 Oracle 데이터베이스에 연결되어야 한다.**

```java
/** @jest-environment node */
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(locations = {
    "classpath*:egovframework/spring/context-*.xml"
})
@Transactional  // 테스트 후 자동 rollback
public class SampleDAOTest {

    @Resource(name = "sampleDAO")
    private SampleDAO sampleDAO;

    @Test
    public void selectList_ROWNUM페이징_정상동작한다() {
        // Arrange
        SampleVO vo = new SampleVO();
        vo.setFirstIndex(0);
        vo.setRecordCountPerPage(10);

        // Act
        List<SampleVO> list = sampleDAO.selectList(vo);

        // Assert
        assertNotNull(list);
        assertTrue(list.size() <= 10);
    }

    @Test
    public void selectDetail_존재하는ID_상세정보반환한다() {
        // Arrange
        String sampleId = "TEST_001";

        // Act
        SampleVO result = sampleDAO.selectDetail(sampleId);

        // Assert
        assertNotNull(result);
        assertEquals(sampleId, result.getSampleId());
    }

    @Test
    @Transactional
    public void insertSample_테스트데이터_삽입성공한다() {
        // Arrange
        SampleVO vo = new SampleVO();
        vo.setSampleId("TEST_" + System.currentTimeMillis());
        vo.setSampleName("테스트명");

        // Act
        sampleDAO.insertSample(vo);

        // Assert: rollback 전에 확인
        SampleVO result = sampleDAO.selectDetail(vo.getSampleId());
        assertNotNull(result);
    }
}
```

---

## 테스트 데이터 규칙

```java
// 테스트 데이터 prefix
String testId = "TST_" + System.currentTimeMillis();

// 테스트 데이터 조회
List<SampleVO> testData = sampleDAO.selectByPrefix("TST_%");

// 테스트 후 정리 (Transactional rollback 활용)
// @Transactional 사용 시 자동으로 롤백됨
```

---

## 테스트 커버리지

목표: **85% 이상**

```bash
# Maven 플러그인으로 커버리지 계산
mvn test jacoco:report

# 리포트 확인
open target/site/jacoco/index.html
```

---

## Maven 테스트 명령

```bash
# 전체 테스트
mvn -q test

# 특정 클래스 테스트
mvn -q test -Dtest=SampleControllerTest
mvn -q test -Dtest=SampleDAOTest

# 특정 메서드 테스트
mvn -q test -Dtest=SampleDAOTest#selectList_ROWNUM페이징_정상동작한다

# 상세 로그
mvn test -X -DfailIfNoTests=false

# 테스트 스킵하고 컴파일만
mvn -q -DskipTests compile

# 테스트 결과 XML 생성
mvn test -Dorg.slf4j.simpleLogger.defaultLogLevel=warn
```

---

## Oracle 11g 연결 전 필수 확인

테스트 실행 전에 반드시:

```bash
# 1. Docker 컨테이너 실행 확인
docker ps | grep oracle

# 2. 포트 연결 확인
nc -zv localhost 1521

# 3. 접속 정보 확인 (globals.properties)
cat src/main/resources/egovframework/egovProps/globals.properties | grep db

# 4. 간단한 SELECT 테스트
# sqlplus를 사용하거나, DAO 테스트로 확인
```

---

## 완료 조건

모든 테스트 완료 전:

```bash
# ✅ 컴파일
mvn -q -DskipTests compile → PASS

# ✅ 테스트
mvn -q test → PASS (실패 0건)
# 출력: 
# BUILD SUCCESS
# Tests run: 15, Failures: 0, Errors: 0

# ✅ 패키지
mvn -q -DskipTests package → PASS
# 생성됨: target/egov-demo-1.0.0.war
```

---

## 체크리스트

- [ ] 모든 메서드에 대해 정상·예외 케이스 테스트 작성
- [ ] Controller 테스트: URL 매핑, view name, ModelMap 속성 검증
- [ ] Service 테스트: 업무 규칙, 정상/예외 케이스
- [ ] DAO 테스트: Oracle 11g 실DB, ROWNUM 페이징, 검색조건
- [ ] 테스트 독립성: 테스트 실행 순서에 무관
- [ ] 한글 검색, 특수문자 처리 테스트 포함
- [ ] 모든 테스트가 `@Transactional + rollback`으로 DB 원상복구
- [ ] `mvn -q test` 통과, 실패 0건
