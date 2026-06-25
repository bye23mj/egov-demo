# egov-developer 항목별 예시 룰

> 목적: egov-developer 에이전트가 전자정부 표준프레임워크 RTE 4.3 기반 프로젝트에서 코딩할 때 참고할 수 있는 항목별 실전 예시 룰이다.  
> 적용 대상: Codex, Claude Code, Cursor, GitHub Copilot, 사내 AI 개발 에이전트  
> 기준 영역: 공통기반, 화면처리, UX처리, 업무처리, 데이터처리, 연계통합, 배치처리, 배치운영환경, 보안

---

# 1. egov-developer 기본 코딩 룰

## 1.1 표준 계층 룰

### Rule

모든 업무 기능은 다음 계층 구조를 기본으로 작성한다.

```text
Controller
→ Service Interface
→ ServiceImpl
→ Mapper 또는 Repository
→ VO / DTO / SearchVO
→ Mapper XML
→ JSP / REST API / JavaScript
→ Validation
→ Exception Handling
→ Test
```

### 나쁜 예

```java
@Controller
public class RequirementController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping("/requirements/save")
    public String save(HttpServletRequest request) {
        String name = request.getParameter("name");

        jdbcTemplate.update("INSERT INTO TB_REQUIREMENT(NAME) VALUES('" + name + "')");

        return "redirect:/requirements";
    }
}
```

### 문제점

```text
1. Controller에 비즈니스 로직과 SQL이 모두 들어 있음
2. SQL Injection 위험
3. Service 계층 없음
4. Mapper 계층 없음
5. Validation 없음
6. Transaction 없음
7. 예외 처리 없음
```

### 좋은 예

```java
@Controller
@RequestMapping("/requirements")
public class RequirementController {

    private final RequirementService requirementService;

    public RequirementController(RequirementService requirementService) {
        this.requirementService = requirementService;
    }

    @PostMapping
    public String save(@Valid RequirementVO requirementVO,
                       BindingResult bindingResult) {
        if (bindingResult.hasErrors()) {
            return "requirement/form";
        }

        requirementService.insertRequirement(requirementVO);
        return "redirect:/requirements";
    }
}
```

```java
public interface RequirementService {
    void insertRequirement(RequirementVO requirementVO);
}
```

```java
@Service
@Transactional
public class RequirementServiceImpl implements RequirementService {

    private final RequirementMapper requirementMapper;

    public RequirementServiceImpl(RequirementMapper requirementMapper) {
        this.requirementMapper = requirementMapper;
    }

    @Override
    public void insertRequirement(RequirementVO requirementVO) {
        requirementMapper.insertRequirement(requirementVO);
    }
}
```

### Codex 지시문

```text
Controller에는 비즈니스 로직과 SQL을 작성하지 말고, Service를 호출하도록 작성한다.
Service Interface와 ServiceImpl을 분리하고, DB 접근은 Mapper 계층으로 분리한다.
```

---

# 2. 공통기반 예시 룰

## 2.1 Logging 룰

### Rule

모든 로그는 `System.out.println`이 아니라 SLF4J Logger를 사용한다.

### 나쁜 예

```java
System.out.println("요구사항 저장 시작");
System.out.println("사용자 ID: " + userId);
```

### 좋은 예

```java
@Slf4j
@Service
public class RequirementServiceImpl implements RequirementService {

    @Override
    public void insertRequirement(RequirementVO requirementVO) {
        log.info("요구사항 저장 시작. requirementId={}", requirementVO.getRequirementId());
    }
}
```

### 보안 로그 주의

```java
// 나쁜 예
log.info("사용자 비밀번호={}", password);

// 좋은 예
log.info("사용자 로그인 시도. userId={}", userId);
```

### Codex 지시문

```text
로그는 SLF4J를 사용한다.
비밀번호, 주민등록번호, 토큰, API Key 등 민감정보는 로그에 남기지 않는다.
```

---

## 2.2 Property 룰

### Rule

파일 경로, 외부 API URL, 업로드 제한 크기, 암호화 키, 연계 URL은 하드코딩하지 않고 properties에서 읽는다.

### 나쁜 예

```java
String uploadPath = "/home/app/upload";
String apiUrl = "https://api.example.com/v1/users";
```

### 좋은 예

```yaml
file:
  upload:
    path: /home/app/upload
    max-size: 10485760

external:
  civil:
    api-url: https://api.example.com/v1
```

```java
@ConfigurationProperties(prefix = "file.upload")
@Getter
@Setter
public class FileUploadProperties {
    private String path;
    private long maxSize;
}
```

### Codex 지시문

```text
환경별로 달라질 수 있는 값은 application.yml 또는 properties에 작성하고, 코드에 하드코딩하지 않는다.
```

---

## 2.3 ID Generation 룰

### Rule

업무 ID, 문서 ID, 신청번호, 배치 실행 ID는 UUID를 임의 사용하기보다 프로젝트 표준 ID 생성 규칙을 따른다.

### 예시 ID 규칙

```text
REQ-202606-0001
UC-202606-0001
SCR-202606-0001
API-202606-0001
TC-202606-0001
BAT-202606-0001
```

### 좋은 예

```java
String requirementId = idGenerationService.nextId("REQ");
requirementVO.setRequirementId(requirementId);
```

### Codex 지시문

```text
업무 식별자는 프로젝트 표준 ID 생성 Service를 사용한다.
요구사항 ID, 유스케이스 ID, 테스트케이스 ID는 추적성을 위해 사람이 읽을 수 있는 형식을 사용한다.
```

---

## 2.4 File Upload 룰

### Rule

파일 업로드 시 확장자, MIME Type, 크기, 저장 경로, 파일명 정규화를 반드시 처리한다.

### 나쁜 예

```java
file.transferTo(new File("/upload/" + file.getOriginalFilename()));
```

### 좋은 예

```java
public AttachmentVO upload(MultipartFile file) {
    validateFile(file);

    String originalFileName = StringUtils.cleanPath(file.getOriginalFilename());
    String storedFileName = UUID.randomUUID() + "_" + originalFileName;

    Path targetPath = Paths.get(fileUploadProperties.getPath())
            .resolve(storedFileName)
            .normalize();

    if (!targetPath.startsWith(fileUploadProperties.getPath())) {
        throw new BusinessException("허용되지 않은 파일 경로입니다.");
    }

    try {
        Files.copy(file.getInputStream(), targetPath);
    } catch (IOException e) {
        throw new SystemException("파일 저장 중 오류가 발생했습니다.", e);
    }

    return AttachmentVO.of(originalFileName, storedFileName, file.getSize());
}
```

### 체크 항목

```text
[ ] 허용 확장자 검증
[ ] MIME Type 검증
[ ] 파일 크기 검증
[ ] 파일명 정규화
[ ] 경로 traversal 방지
[ ] 저장 파일명 난수화
[ ] 다운로드 시 권한 확인
```

### Codex 지시문

```text
파일 업로드 기능 작성 시 확장자, MIME Type, 크기, 경로 traversal을 검증하고 저장 파일명은 난수화한다.
```

---

## 2.5 Crypto 룰

### Rule

개인정보, 토큰, 인증키, 연계 비밀값은 평문 저장하지 않는다.

### 암호화 대상 예시

```text
주민등록번호
휴대전화번호
이메일
API Token
연계 인증키
개인식별번호
```

### 나쁜 예

```java
userVO.setResidentNo(request.getResidentNo());
```

### 좋은 예

```java
userVO.setResidentNo(cryptoService.encrypt(request.getResidentNo()));
```

### Codex 지시문

```text
개인정보와 인증정보는 저장 전 암호화하고, 조회 시 필요한 경우에만 복호화한다.
로그에는 복호화된 값을 남기지 않는다.
```

---

# 3. 화면처리 예시 룰

## 3.1 Controller 룰

### Rule

Controller는 요청 매핑, 입력 검증, Service 호출, Model 구성만 담당한다.

### 좋은 예

```java
@Controller
@RequestMapping("/requirements")
public class RequirementController {

    private final RequirementService requirementService;

    @GetMapping
    public String list(@ModelAttribute RequirementSearchVO searchVO, Model model) {
        model.addAttribute("resultList", requirementService.selectRequirementList(searchVO));
        return "requirement/list";
    }

    @GetMapping("/{requirementId}")
    public String detail(@PathVariable String requirementId, Model model) {
        model.addAttribute("requirement", requirementService.selectRequirement(requirementId));
        return "requirement/detail";
    }
}
```

### Codex 지시문

```text
Controller는 thin controller로 작성한다.
비즈니스 규칙, 상태 전이, DB 처리, 외부 API 호출은 Service 계층으로 위임한다.
```

---

## 3.2 Validation 룰

### Rule

입력값 검증은 Controller 내부 if문으로 길게 작성하지 말고 Bean Validation 또는 Validator로 분리한다.

### VO 예시

```java
@Getter
@Setter
public class RequirementVO {

    private String requirementId;

    @NotBlank(message = "요구사항명은 필수입니다.")
    @Size(max = 200, message = "요구사항명은 200자를 초과할 수 없습니다.")
    private String requirementName;

    @NotBlank(message = "요구사항 유형은 필수입니다.")
    private String requirementType;

    @Size(max = 4000, message = "요구사항 설명은 4000자를 초과할 수 없습니다.")
    private String description;
}
```

### Controller 예시

```java
@PostMapping
public String save(@Valid RequirementVO requirementVO,
                   BindingResult bindingResult) {
    if (bindingResult.hasErrors()) {
        return "requirement/form";
    }

    requirementService.insertRequirement(requirementVO);
    return "redirect:/requirements";
}
```

### Codex 지시문

```text
등록/수정 요청 객체에는 Bean Validation을 적용하고, Controller에서 BindingResult를 확인한다.
```

---

## 3.3 Ajax API 룰

### Rule

화면 반환 Controller와 JSON API는 분리한다.

### 좋은 예

```java
@RestController
@RequestMapping("/api/requirements")
public class RequirementApiController {

    private final RequirementService requirementService;

    @GetMapping("/{requirementId}")
    public RequirementVO detail(@PathVariable String requirementId) {
        return requirementService.selectRequirement(requirementId);
    }
}
```

### Codex 지시문

```text
JSP 화면 반환 Controller와 Ajax/REST API Controller를 분리한다.
API 응답은 공통 응답 포맷을 사용한다.
```

---

# 4. UX처리 예시 룰

## 4.1 버튼 권한 렌더링 룰

### Rule

권한 없는 버튼은 화면에 표시하지 않는다. 단, 서버 API 권한 검사도 반드시 함께 수행한다.

### JSP 예시

```jsp
<c:if test="${buttonAuth.create}">
    <button type="button" id="createBtn" class="btn btn-primary">등록</button>
</c:if>

<c:if test="${buttonAuth.delete}">
    <button type="button" id="deleteBtn" class="btn btn-danger">삭제</button>
</c:if>
```

### Controller 예시

```java
@GetMapping
public String list(@ModelAttribute RequirementSearchVO searchVO, Model model) {
    model.addAttribute("resultList", requirementService.selectRequirementList(searchVO));
    model.addAttribute("buttonAuth", menuAuthService.selectButtonAuth("MENU_REQ_001"));
    return "requirement/list";
}
```

### Codex 지시문

```text
버튼 권한은 서버에서 계산하여 View에 전달한다.
JavaScript로만 버튼을 숨기는 방식은 보안으로 인정하지 않는다.
```

---

## 4.2 JavaScript 모듈 분리 룰

### Rule

JSP 안에 긴 JavaScript를 작성하지 않고 화면별 JS 파일로 분리한다.

### 나쁜 예

```jsp
<script>
function save() {
    $.ajax({
        url: '/requirements',
        method: 'POST',
        data: $('#form').serialize()
    });
}
</script>
```

### 좋은 예

```text
/static/js/requirement/requirement-form.js
```

```javascript
const RequirementForm = {
    init() {
        $('#saveBtn').on('click', this.save);
    },

    save() {
        if (!confirm('저장하시겠습니까?')) {
            return;
        }

        $.ajax({
            url: '/requirements',
            method: 'POST',
            data: $('#requirementForm').serialize()
        }).done(() => {
            location.href = '/requirements';
        }).fail((xhr) => {
            alert(xhr.responseJSON?.message || '저장 중 오류가 발생했습니다.');
        });
    }
};

$(document).ready(() => RequirementForm.init());
```

### Codex 지시문

```text
JSP에는 화면 구조만 작성하고, JavaScript 로직은 화면별 JS 파일로 분리한다.
```

---

## 4.3 오류 메시지 UX 룰

### Rule

사용자 입력 오류는 필드 가까이에 표시한다.

### JSP 예시

```jsp
<form:input path="requirementName" cssClass="form-control"/>
<form:errors path="requirementName" cssClass="text-danger"/>
```

### Codex 지시문

```text
Validation 오류는 필드 하단에 표시하고, 사용자에게 수정 방법을 알 수 있는 메시지를 제공한다.
```

---

# 5. 업무처리 예시 룰

## 5.1 상태 전이 룰

### Rule

상태 변경은 단순 update가 아니라 WorkflowService에서 상태 전이 가능 여부를 검증한 뒤 처리한다.

### 상태 예시

```text
작성중
→ 내부검토
→ 보완요청
→ 보완완료
→ 고객검토
→ 승인
→ 기준선등록
```

### 좋은 예

```java
@Service
@Transactional
public class RequirementWorkflowServiceImpl implements RequirementWorkflowService {

    private final RequirementMapper requirementMapper;
    private final RequirementHistoryMapper requirementHistoryMapper;

    @Override
    public void requestReview(String requirementId, String userId) {
        RequirementVO requirement = requirementMapper.selectRequirement(requirementId);

        if (!"DRAFT".equals(requirement.getStatus())) {
            throw new BusinessException("작성중 상태에서만 내부검토를 요청할 수 있습니다.");
        }

        requirementMapper.updateStatus(requirementId, "INTERNAL_REVIEW");
        requirementHistoryMapper.insertHistory(
                RequirementHistoryVO.of(requirementId, "INTERNAL_REVIEW", userId, "내부검토 요청")
        );
    }
}
```

### Codex 지시문

```text
승인, 반려, 보완요청 같은 상태 변경은 WorkflowService에 작성하고, 모든 상태 변경 이력을 저장한다.
```

---

## 5.2 BusinessException 룰

### Rule

업무 규칙 위반은 `BusinessException`, 시스템 오류는 `SystemException`으로 구분한다.

### 좋은 예

```java
if (!user.hasRole("ROLE_PM")) {
    throw new BusinessException("승인 권한이 없습니다.");
}
```

```java
try {
    externalClient.send(request);
} catch (IOException e) {
    throw new SystemException("외부 시스템 연계 중 오류가 발생했습니다.", e);
}
```

### Codex 지시문

```text
사용자 조치가 가능한 업무 오류는 BusinessException으로 처리하고, 시스템 장애는 SystemException으로 처리한다.
```

---

## 5.3 변경 이력 룰

### Rule

중요 업무 데이터의 상태 변경, 승인, 삭제, 보완요청은 이력 테이블에 기록한다.

### 이력 테이블 예시

```sql
CREATE TABLE TB_REQUIREMENT_HISTORY (
    HISTORY_ID       VARCHAR(50) PRIMARY KEY,
    REQUIREMENT_ID   VARCHAR(50) NOT NULL,
    BEFORE_STATUS    VARCHAR(30),
    AFTER_STATUS     VARCHAR(30),
    ACTION_TYPE      VARCHAR(30),
    ACTION_COMMENT   VARCHAR(1000),
    ACTION_USER_ID   VARCHAR(50),
    ACTION_AT        TIMESTAMP
);
```

### Codex 지시문

```text
상태 변경 기능 작성 시 반드시 이력 테이블 저장 로직을 포함한다.
```

---

# 6. 데이터처리 예시 룰

## 6.1 MyBatis Mapper 룰

### Rule

SQL은 Mapper XML에 작성하고, Java 코드에 직접 문자열 SQL을 작성하지 않는다.

### Mapper Interface

```java
@Mapper
public interface RequirementMapper {

    List<RequirementVO> selectRequirementList(RequirementSearchVO searchVO);

    RequirementVO selectRequirement(String requirementId);

    int insertRequirement(RequirementVO requirementVO);

    int updateRequirement(RequirementVO requirementVO);

    int deleteRequirement(String requirementId);
}
```

### Mapper XML

```xml
<select id="selectRequirementList"
        parameterType="RequirementSearchVO"
        resultType="RequirementVO">
    SELECT
        REQUIREMENT_ID,
        REQUIREMENT_NAME,
        REQUIREMENT_TYPE,
        STATUS,
        OWNER_ID,
        CREATED_AT
    FROM TB_REQUIREMENT
    WHERE 1 = 1
    <if test="requirementName != null and requirementName != ''">
        AND REQUIREMENT_NAME LIKE CONCAT('%', #{requirementName}, '%')
    </if>
    <if test="status != null and status != ''">
        AND STATUS = #{status}
    </if>
    ORDER BY CREATED_AT DESC
</select>
```

### Codex 지시문

```text
DB 처리는 MyBatis Mapper와 Mapper XML로 작성한다.
검색조건은 Dynamic SQL로 작성하고 null/empty 조건을 고려한다.
```

---

## 6.2 Transaction 룰

### Rule

트랜잭션은 Controller가 아니라 Service 계층에서 처리한다.

### 좋은 예

```java
@Service
@Transactional
public class RequirementServiceImpl implements RequirementService {

    @Override
    public void insertRequirement(RequirementVO requirementVO) {
        requirementMapper.insertRequirement(requirementVO);
        requirementHistoryMapper.insertHistory(...);
    }

    @Transactional(readOnly = true)
    @Override
    public RequirementVO selectRequirement(String requirementId) {
        return requirementMapper.selectRequirement(requirementId);
    }
}
```

### Codex 지시문

```text
등록, 수정, 삭제, 승인 로직은 @Transactional을 적용하고, 조회는 readOnly=true를 적용한다.
```

---

## 6.3 SearchVO 룰

### Rule

검색 조건은 별도 SearchVO로 분리한다.

### 좋은 예

```java
@Getter
@Setter
public class RequirementSearchVO extends PaginationVO {

    private String requirementName;
    private String requirementType;
    private String status;
    private String ownerId;
    private LocalDate startDate;
    private LocalDate endDate;
}
```

### Codex 지시문

```text
목록 조회 기능은 SearchVO를 사용하고, 페이징과 정렬 조건을 포함한다.
```

---

# 7. 연계통합 예시 룰

## 7.1 External Client 룰

### Rule

외부 API 호출은 업무 Service에 직접 작성하지 않고 Client/Adapter 클래스로 분리한다.

### 나쁜 예

```java
@Service
public class RequirementServiceImpl {

    public void sendToExternalSystem(RequirementVO requirementVO) {
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.postForObject("https://api.example.com/req", requirementVO, String.class);
    }
}
```

### 좋은 예

```java
@Component
public class ExternalRequirementClient {

    private final RestClient restClient;

    public ExternalRequirementClient(RestClient.Builder builder,
                                     ExternalApiProperties properties) {
        this.restClient = builder
                .baseUrl(properties.getBaseUrl())
                .build();
    }

    public ExternalRequirementResponse send(ExternalRequirementRequest request) {
        return restClient.post()
                .uri("/requirements")
                .body(request)
                .retrieve()
                .body(ExternalRequirementResponse.class);
    }
}
```

### Codex 지시문

```text
외부 API 호출은 Client 또는 Adapter 클래스로 분리하고, 업무 Service는 해당 Client를 호출하도록 작성한다.
```

---

## 7.2 연계 로그 룰

### Rule

외부 시스템 연계 요청/응답/오류는 연계 로그 테이블에 저장한다.

### 테이블 예시

```sql
CREATE TABLE TB_INTEGRATION_LOG (
    LOG_ID            VARCHAR(50) PRIMARY KEY,
    SYSTEM_CODE       VARCHAR(50),
    API_NAME          VARCHAR(100),
    REQUEST_BODY      TEXT,
    RESPONSE_BODY     TEXT,
    RESULT_CODE       VARCHAR(30),
    ERROR_MESSAGE     TEXT,
    REQUEST_AT        TIMESTAMP,
    RESPONSE_AT       TIMESTAMP
);
```

### Codex 지시문

```text
외부 연계 기능 작성 시 요청/응답/오류 이력을 integration_log 테이블에 저장한다.
민감정보는 마스킹 후 저장한다.
```

---

## 7.3 Timeout/Retry 룰

### Rule

외부 API 호출에는 Timeout과 Retry 정책을 정의한다.

### Codex 지시문

```text
외부 API 호출에는 connection timeout, read timeout, retry 정책을 포함한다.
장애 발생 시 BusinessException 또는 SystemException으로 변환한다.
```

---

# 8. 배치처리 예시 룰

## 8.1 Job/Step 분리 룰

### Rule

배치는 Job, Step, Reader, Processor, Writer 또는 Tasklet으로 분리한다.

### 좋은 예

```java
@Configuration
public class RequirementSyncJobConfig {

    @Bean
    public Job requirementSyncJob(JobRepository jobRepository,
                                  Step collectRequirementStep,
                                  Step convertRequirementStep,
                                  Step notifyResultStep) {
        return new JobBuilder("requirementSyncJob", jobRepository)
                .start(collectRequirementStep)
                .next(convertRequirementStep)
                .next(notifyResultStep)
                .build();
    }
}
```

### Codex 지시문

```text
배치 기능은 Job과 Step으로 분리하고, 각 Step의 책임을 명확히 한다.
```

---

## 8.2 Chunk 기반 처리 룰

### Rule

대량 데이터 처리는 Chunk 기반으로 처리한다.

### 예시

```java
@Bean
public Step requirementProcessStep(JobRepository jobRepository,
                                   PlatformTransactionManager transactionManager,
                                   ItemReader<RequirementVO> reader,
                                   ItemProcessor<RequirementVO, RequirementVO> processor,
                                   ItemWriter<RequirementVO> writer) {
    return new StepBuilder("requirementProcessStep", jobRepository)
            .<RequirementVO, RequirementVO>chunk(100, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .build();
}
```

### Codex 지시문

```text
대량 데이터 배치는 chunk 기반으로 작성하고 chunk size를 명시한다.
```

---

## 8.3 Retry/Skip 룰

### Rule

외부 연계나 파일 처리처럼 실패 가능성이 높은 배치는 Retry/Skip 정책을 둔다.

### Codex 지시문

```text
외부 연계 배치에는 Retry 3회 정책을 적용하고, 특정 예외는 Skip 처리한다.
Skip된 데이터는 실패 이력에 저장한다.
```

---

## 8.4 Batch History 룰

### Rule

배치 실행 결과는 이력 테이블에 저장한다.

### 테이블 예시

```sql
CREATE TABLE TB_BATCH_HISTORY (
    EXECUTION_ID      VARCHAR(50) PRIMARY KEY,
    JOB_NAME          VARCHAR(100),
    JOB_PARAMETER     TEXT,
    STATUS            VARCHAR(30),
    START_TIME        TIMESTAMP,
    END_TIME          TIMESTAMP,
    READ_COUNT        INTEGER,
    WRITE_COUNT       INTEGER,
    SKIP_COUNT        INTEGER,
    ERROR_MESSAGE     TEXT
);
```

### Codex 지시문

```text
배치 실행 후 실행 상태, 처리 건수, 실패 건수, 오류 메시지를 배치 이력에 저장한다.
```

---

# 9. 배치운영환경 예시 룰

## 9.1 Job 등록 룰

### Rule

운영자가 배치 Job을 조회, 실행, 중지, 재실행할 수 있도록 Job 등록 정보를 관리한다.

### 테이블 예시

```sql
CREATE TABLE TB_BATCH_JOB_MANAGEMENT (
    JOB_ID          VARCHAR(50) PRIMARY KEY,
    JOB_NAME        VARCHAR(100) NOT NULL,
    JOB_DESC        VARCHAR(500),
    USE_YN          CHAR(1) DEFAULT 'Y',
    EXEC_AUTH_ROLE  VARCHAR(100),
    CREATED_AT      TIMESTAMP
);
```

### Codex 지시문

```text
배치 Job은 운영환경에서 관리할 수 있도록 Job ID, Job Name, 설명, 사용여부, 실행권한을 저장한다.
```

---

## 9.2 운영 API 룰

### Rule

배치운영환경에는 최소한 목록, 상세, 실행, 재실행, 이력 조회 API를 제공한다.

### API 예시

```text
GET  /admin/batch/jobs
GET  /admin/batch/jobs/{jobId}
POST /admin/batch/jobs/{jobId}/run
POST /admin/batch/executions/{executionId}/rerun
GET  /admin/batch/executions
GET  /admin/batch/executions/{executionId}
```

### Codex 지시문

```text
배치운영환경 API는 ROLE_ADMIN 또는 ROLE_OPERATOR만 접근 가능하도록 권한 정보를 생성한다.
```

---

## 9.3 실패 알림 룰

### Rule

배치 실패 시 Slack 또는 Mail로 운영자에게 알린다.

### 알림 예시

```text
[배치 실패 알림]

Job: requirementSyncJob
Execution ID: BAT-202606-0001
Status: FAILED
Error: Confluence API Timeout
실행시간: 2026-06-14 10:00:00 ~ 10:05:12
```

### Codex 지시문

```text
배치 실패 시 Slack 또는 Mail 알림을 발송하는 후처리 로직을 포함한다.
```

---

# 10. 보안 예시 룰

## 10.1 메뉴 등록 룰

### Rule

신규 화면 기능을 개발하면 메뉴 등록 정보를 반드시 함께 생성한다.

### 예시

| 메뉴 ID | 상위 메뉴 ID | 메뉴명 | URL | 정렬순서 | 사용여부 |
|---|---|---|---|---:|---|
| MENU_REQ_001 | MENU_PROJECT | 요구사항 관리 | /requirements | 10 | Y |

### Codex 지시문

```text
신규 화면 기능을 생성한 경우 메뉴 등록 정보를 함께 출력한다.
```

---

## 10.2 URL/프로그램 등록 룰

### Rule

신규 Controller URL은 프로그램 또는 보호 자원으로 등록한다.

### 예시

| 프로그램 ID | URL Pattern | 설명 | 권한 필요 |
|---|---|---|---|
| PGM_REQ_LIST | /requirements | 요구사항 목록 | Y |
| PGM_REQ_DETAIL | /requirements/* | 요구사항 상세 | Y |
| PGM_REQ_SAVE | /requirements/save | 요구사항 저장 | Y |
| PGM_REQ_DELETE | /requirements/*/delete | 요구사항 삭제 | Y |
| PGM_REQ_APPROVE | /requirements/*/approve | 요구사항 승인 | Y |

### Codex 지시문

```text
Controller URL을 생성한 뒤 URL/프로그램 등록 표를 함께 생성한다.
```

---

## 10.3 Role별 URL 권한 룰

### Rule

각 URL에 접근 가능한 Role을 명시한다.

### 예시

| URL Pattern | 허용 Role |
|---|---|
| /requirements | ROLE_VIEWER 이상 |
| /requirements/new | ROLE_ANALYST, ROLE_PL, ROLE_PM, ROLE_ADMIN |
| /requirements/save | ROLE_ANALYST, ROLE_PL, ROLE_PM, ROLE_ADMIN |
| /requirements/*/delete | ROLE_PM, ROLE_ADMIN |
| /requirements/*/approve | ROLE_PM, ROLE_CUSTOMER, ROLE_ADMIN |

### Codex 지시문

```text
신규 URL별 허용 Role을 명시하고, 조회/등록/수정/삭제/승인 권한을 분리한다.
```

---

## 10.4 버튼 권한 룰

### Rule

화면 버튼도 권한별로 제어한다.

### 예시

| 버튼 | 기능 ID | 허용 Role |
|---|---|---|
| 등록 | BTN_REQ_CREATE | ROLE_ANALYST, ROLE_PL, ROLE_PM, ROLE_ADMIN |
| 수정 | BTN_REQ_UPDATE | ROLE_ANALYST, ROLE_PL, ROLE_PM, ROLE_ADMIN |
| 삭제 | BTN_REQ_DELETE | ROLE_PM, ROLE_ADMIN |
| 승인 | BTN_REQ_APPROVE | ROLE_PM, ROLE_CUSTOMER, ROLE_ADMIN |

### Codex 지시문

```text
화면 버튼 권한 표를 생성하고, View에서는 서버에서 전달한 buttonAuth를 기준으로 버튼을 렌더링한다.
```

---

## 10.5 접근 테스트 룰

### Rule

기능 개발 후 Role별 접근 가능 여부를 테스트한다.

### 예시

| Role | 목록 | 상세 | 등록 | 수정 | 삭제 | 승인 |
|---|---|---|---|---|---|---|
| ROLE_VIEWER | 가능 | 가능 | 불가 | 불가 | 불가 | 불가 |
| ROLE_ANALYST | 가능 | 가능 | 가능 | 가능 | 불가 | 불가 |
| ROLE_PM | 가능 | 가능 | 가능 | 가능 | 가능 | 가능 |
| ROLE_CUSTOMER | 가능 | 가능 | 불가 | 불가 | 불가 | 가능 |
| ROLE_ADMIN | 가능 | 가능 | 가능 | 가능 | 가능 | 가능 |

### Codex 지시문

```text
기능 개발 완료 후 Role별 접근 테스트 시나리오를 표로 생성한다.
```

---

# 11. 테스트 예시 룰

## 11.1 Controller Test 룰

### Rule

Controller 테스트는 요청 URL, 파라미터, 권한, Validation 오류를 검증한다.

### Codex 지시문

```text
Controller 테스트에서는 목록/상세/등록/수정/삭제 URL과 Validation 오류를 검증한다.
권한별 접근 가능 여부도 테스트 시나리오에 포함한다.
```

---

## 11.2 Service Test 룰

### Rule

Service 테스트는 업무 규칙과 상태 전이를 검증한다.

### Codex 지시문

```text
Service 테스트에서는 정상 처리, 잘못된 상태 전이, 권한 오류, 이력 저장 여부를 검증한다.
```

---

## 11.3 Mapper Test 룰

### Rule

Mapper 테스트는 SQL 결과와 Dynamic SQL 조건을 검증한다.

### Codex 지시문

```text
Mapper 테스트에서는 검색조건별 조회 결과, 등록/수정/삭제 결과, null/empty 조건을 검증한다.
```

---

# 12. egov-developer 최종 출력 룰

egov-developer는 기능 코딩 후 반드시 아래 형식으로 결과를 출력한다.

```markdown
# 생성 결과

## 1. 생성 파일

| 파일 | 설명 |
|---|---|

## 2. 주요 구현 내용

## 3. DB 변경사항

## 4. 메뉴 등록 정보

| 메뉴 ID | 상위 메뉴 ID | 메뉴명 | URL | 사용여부 |
|---|---|---|---|---|

## 5. URL/프로그램 등록 정보

| 프로그램 ID | URL Pattern | 설명 | 권한 필요 |
|---|---|---|---|

## 6. Role별 URL 권한

| URL Pattern | 허용 Role |
|---|---|

## 7. 버튼 권한

| 버튼 | 기능 ID | 허용 Role |
|---|---|---|

## 8. 테스트 시나리오

| 테스트 ID | 내용 | 예상 결과 |
|---|---|---|

## 9. 접근권한 테스트

| Role | 목록 | 상세 | 등록 | 수정 | 삭제 | 승인 |
|---|---|---|---|---|---|---|

## 10. 추가 확인사항
```

---

# 13. 기능별 미니 프롬프트 예시

## 13.1 요구사항 관리 기능

```text
egov-developer로 동작해줘.
전자정부프레임워크 RTE 4.3 기준으로 요구사항 관리 CRUD를 작성해줘.

반드시 적용:
- Controller, Service, ServiceImpl, Mapper, Mapper XML 분리
- Validation 적용
- Transaction 적용
- BusinessException 적용
- 메뉴 등록 정보 생성
- URL 권한 정보 생성
- 버튼 권한 정보 생성
- Role별 접근 테스트 시나리오 생성
```

## 13.2 승인 기능

```text
egov-developer로 동작해줘.
요구사항 승인 기능을 작성해줘.

규칙:
- 상태 전이는 WorkflowService에서 처리
- 작성중 → 내부검토 → 고객검토 → 승인 흐름 적용
- 잘못된 상태 전이는 BusinessException 발생
- 승인 이력 저장
- ROLE_PM, ROLE_CUSTOMER, ROLE_ADMIN만 승인 가능
- 승인 버튼 권한 정보 생성
```

## 13.3 파일 업로드 기능

```text
egov-developer로 동작해줘.
전자정부 공통기반 File Upload/Download 기준으로 산출물 첨부 기능을 작성해줘.

규칙:
- 확장자 검증
- MIME Type 검증
- 파일 크기 검증
- 경로 traversal 방지
- 저장 파일명 난수화
- 다운로드 시 권한 확인
- 첨부파일 메타데이터 저장
```

## 13.4 외부 REST 연계 기능

```text
egov-developer로 동작해줘.
전자정부 연계통합 기준으로 외부 민원시스템 REST 연계를 작성해줘.

규칙:
- Client/Adapter 분리
- 요청/응답 DTO 분리
- API URL은 properties에서 읽기
- Timeout/Retry 처리
- 연계 로그 저장
- 민감정보 마스킹
- Swagger 문서 생성
```

## 13.5 배치 기능

```text
egov-developer로 동작해줘.
전자정부 배치처리 기준으로 요구사항 문서 동기화 배치를 작성해줘.

규칙:
- Job/Step/Reader/Processor/Writer 분리
- Retry 3회
- Skip 이력 저장
- Batch History 저장
- 실패 시 Slack 알림
- 배치운영환경 API 생성
```

---

# 14. 최종 요약

egov-developer가 코딩할 때 반드시 기억해야 할 핵심은 다음이다.

```text
코드만 만들지 말고,
전자정부 표준 운영에 필요한 메뉴, URL, 권한, 버튼, 테스트, 이력까지 함께 만든다.
```

즉, 기능 개발은 다음 흐름으로 완료된다.

```text
요구사항
→ Controller/Service/Mapper/View 코드 생성
→ Validation/Transaction/Exception 적용
→ 메뉴 등록 정보 생성
→ URL/Role 권한 정보 생성
→ 버튼 권한 정보 생성
→ 테스트 시나리오 생성
→ 접근권한 테스트 생성
→ 운영 반영 가능 상태
```
