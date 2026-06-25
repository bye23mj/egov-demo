# Doc2Claude Manager 설계서

## 1. 개요

**Doc2Claude Manager**는 정부기관 전자정부 표준프레임워크 프로젝트에서 작성되는 산출물 문서를 자동으로 수집하고, Claude가 이해하기 쉬운 Markdown 형식으로 변환한 뒤, Jira 일정 상태에 따라 요구사항 확인, 개발, 테스트, 통합테스트, 배포 단계에서 자동으로 참조할 수 있도록 지원하는 문서관리 프로그램이다.

지원 대상 문서는 다음과 같다.

- HWPX
- DOC / DOCX
- XLS / XLSX
- PPT / PPTX
- 선택 확장: PDF

본 프로그램은 단순 문서 변환기가 아니라, 프로젝트 산출물을 **AI가 활용 가능한 지식 컨텍스트**로 정규화하고, Jira + Confluence + Slack과 연계하여 프로젝트 수행 흐름에 통합하는 것을 목표로 한다.

---

## 2. 목표

### 2.1 핵심 목표

```text
프로젝트 산출물 문서
→ Markdown 자동 변환
→ 요구사항/설계/테스트 정보 추출
→ Jira 일정 상태와 연결
→ Claude용 Context 생성
→ Confluence 저장
→ Slack 알림
→ 개발/테스트/배포 단계에서 활용
```

### 2.2 기대 효과

| 구분 | 기대 효과 |
|---|---|
| 요구사항 관리 | 회의록, 요구사항정의서, 화면설계서를 자동 참조하여 누락 최소화 |
| 개발 생산성 | Claude가 관련 설계 문서를 Markdown으로 이해하여 코드 작성 보조 |
| 테스트 품질 | 요구사항과 테스트케이스 연결 자동화 |
| 일정관리 | Jira 상태에 따라 필요한 문서를 자동으로 Context화 |
| 문서관리 | Confluence에 원본 문서와 변환 Markdown을 함께 관리 |
| 커뮤니케이션 | Slack으로 문서 변환, 변경, Context 생성 결과 알림 |

---

## 3. 전체 아키텍처

```text
Confluence / 로컬 문서 / 공유폴더
        ↓
Document Collector
        ↓
Document Converter
        ↓
Markdown Normalizer
        ↓
AI Context Extractor
        ↓
Markdown Repository
        ↓
Jira + Confluence + Slack 통합
        ↓
Claude / Codex / Gemini 작업 컨텍스트 제공
```

---

## 4. 주요 컴포넌트

```text
doc2claude-manager
├─ collector
│  ├─ ConfluenceAttachmentCollector
│  ├─ LocalFolderCollector
│  └─ JiraLinkedDocumentCollector
├─ converter
│  ├─ HwpxToMarkdownConverter
│  ├─ WordToMarkdownConverter
│  ├─ ExcelToMarkdownConverter
│  ├─ PowerPointToMarkdownConverter
│  └─ TikaFallbackConverter
├─ normalizer
│  ├─ MarkdownCleaner
│  ├─ HeadingNormalizer
│  ├─ TableNormalizer
│  └─ MetadataAppender
├─ extractor
│  ├─ RequirementExtractor
│  ├─ DesignExtractor
│  ├─ TestCaseExtractor
│  └─ DeploymentChecklistExtractor
├─ integration
│  ├─ JiraClient
│  ├─ ConfluenceClient
│  ├─ SlackNotifier
│  └─ ClaudeContextPublisher
└─ scheduler
   ├─ JiraScheduleWatcher
   ├─ DocumentSyncJob
   └─ PhaseContextBuildJob
```

---

## 5. 지원 파일 포맷

| 포맷 | 처리 방식 | 권장 기술 |
|---|---|---|
| `.hwpx` | ZIP 내부 XML 파싱 또는 HWPX 라이브러리 사용 | hwpxlib, XML Parser |
| `.doc` | 텍스트 추출 | Apache Tika |
| `.docx` | 제목, 본문, 표 추출 | Apache POI, Apache Tika |
| `.xls` | 시트별 표 추출 | Apache POI |
| `.xlsx` | 시트별 Markdown Table 변환 | Apache POI |
| `.ppt` | 슬라이드 텍스트 추출 | Apache Tika |
| `.pptx` | 슬라이드별 제목, 본문, 표 추출 | Apache POI |
| `.pdf` | 선택 확장, 텍스트 추출 | Apache PDFBox, Apache Tika |

---

## 6. 문서 수집 흐름

```text
1. Confluence Space 또는 지정 폴더에서 문서 검색
2. 신규/변경 문서 감지
3. 원본 파일 다운로드
4. 파일 해시 계산
5. 이전 변환 결과와 비교
6. 변경된 문서만 Markdown 재생성
7. Confluence 또는 Git 저장소에 Markdown 저장
8. 관련 Jira 이슈에 변환본 링크 연결
9. Slack으로 변환 결과 알림
```

---

## 7. Markdown 변환 흐름

```text
원본 문서
→ 텍스트/표/슬라이드/시트 추출
→ 제목 구조 정규화
→ Markdown 변환
→ 메타데이터 추가
→ 요구사항/설계/테스트 태그 부여
→ Claude용 Context 파일 생성
```

### 7.1 Markdown 변환 결과 예시

```markdown
---
source_file: 요구사항정의서.hwpx
document_type: requirement
project: 전자정부 표준프레임워크 기반 구축사업
jira_epic: GOV-EPIC-001
converted_at: 2026-06-06T10:00:00+09:00
hash: a8f3...
---

# 요구사항정의서

## REQ-FN-001 민원 신청서 작성

### 요구사항 설명

사용자는 민원 신청서를 작성할 수 있어야 한다.

### 관련 화면

- SCR-001 민원 신청서 작성 화면

### 관련 API

- API-001 신청서 저장 API

### 관련 테스트

- TC-001 신청서 작성 정상 케이스
- TC-002 필수값 누락 예외 케이스
```

---

## 8. Jira 일정 기반 자동 참조 흐름

### 8.1 Jira 단계별 참조 문서

| Jira 단계 | 자동 참조 문서 | Claude 활용 |
|---|---|---|
| 요구사항 확인 | 요구사항정의서, 회의록, 요구사항추적표 | 요구사항 요약, 누락 질문 도출 |
| 분석/설계 | 유스케이스명세서, 화면설계서, API설계서, DB설계서 | 컴포넌트 설계, API 설계 검토 |
| 개발 | 상세설계서, 프로그램설계서, 표준코딩가이드 | 구현 계획, 코드 생성, 리팩터링 |
| 단위테스트 | 단위테스트케이스, 요구사항추적표 | 테스트 코드 생성 |
| 통합테스트 | 통합테스트시나리오, 인터페이스설계서 | 통합 테스트 시나리오 검토 |
| 배포 | 배포계획서, 운영전환계획서, 체크리스트 | 배포 전 점검, 릴리즈 노트 작성 |

### 8.2 자동화 예시

```text
Jira 이슈 GOV-123 상태가 "개발중"으로 변경됨
→ 관련 Requirement ID 확인
→ Confluence에서 연결 문서 검색
→ Markdown 변환본 최신 여부 확인
→ Claude Context 생성
→ Slack 개발 채널에 알림
→ 개발자가 Claude Code에서 Context 참조
```

---

## 9. Confluence 통합 설계

Confluence는 공식 산출물 저장소로 사용한다.

### 9.1 Space 구조

```text
전자정부프로젝트 Space
├─ 00_사업관리
├─ 01_요구사항
├─ 02_분석
├─ 03_설계
├─ 04_개발
├─ 05_테스트
├─ 06_배포_운영전환
└─ 99_AI_Context
```

### 9.2 Markdown 변환 결과 저장 구조

```text
99_AI_Context
├─ requirements/
│  ├─ REQ-FN-001.md
│  └─ REQ-FN-002.md
├─ design/
│  ├─ component-design.md
│  ├─ api-design.md
│  └─ database-design.md
├─ test/
│  ├─ unit-test-context.md
│  └─ integration-test-context.md
└─ release/
   └─ deployment-checklist.md
```

---

## 10. Slack 통합 설계

Slack은 알림과 승인 요청 채널로 사용한다.

### 10.1 Slack 채널 구성

| 채널 | 용도 |
|---|---|
| `#pjt-doc-sync` | 문서 변환 결과 알림 |
| `#pjt-requirements` | 요구사항 검토 알림 |
| `#pjt-dev` | 개발 단계 Context 생성 알림 |
| `#pjt-test` | 테스트 문서 참조 알림 |
| `#pjt-release` | 배포 체크리스트 알림 |

### 10.2 Slack 알림 예시

```text
[문서 변환 완료]
- 원본: 요구사항정의서.hwpx
- 변환본: REQ-FN-001.md
- 관련 Jira: GOV-123
- 단계: 개발
- Claude Context: 생성 완료
```

---

## 11. 데이터 모델

### 11.1 원본 문서 테이블

```sql
CREATE TABLE document_source (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_key VARCHAR(50) NOT NULL,
    source_type VARCHAR(30) NOT NULL,
    source_url TEXT,
    file_name VARCHAR(500) NOT NULL,
    file_ext VARCHAR(20) NOT NULL,
    file_hash VARCHAR(128) NOT NULL,
    document_type VARCHAR(50),
    jira_issue_key VARCHAR(50),
    confluence_page_id VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 11.2 Markdown 변환 결과 테이블

```sql
CREATE TABLE markdown_document (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source_document_id BIGINT NOT NULL,
    markdown_path TEXT NOT NULL,
    title VARCHAR(500),
    summary TEXT,
    requirement_ids TEXT,
    usecase_ids TEXT,
    api_ids TEXT,
    testcase_ids TEXT,
    converted_at TIMESTAMP,
    FOREIGN KEY (source_document_id) REFERENCES document_source(id)
);
```

### 11.3 Jira 단계별 Context 테이블

```sql
CREATE TABLE phase_context (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_key VARCHAR(50) NOT NULL,
    jira_issue_key VARCHAR(50) NOT NULL,
    phase VARCHAR(50) NOT NULL,
    context_markdown_path TEXT NOT NULL,
    generated_at TIMESTAMP
);
```

---

## 12. Spring Boot 구현 설계

### 12.1 권장 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | Java 17/21, Spring Boot 3.x |
| Batch | Spring Batch, Quartz |
| 문서 파싱 | Apache Tika, Apache POI, hwpxlib/custom XML parser |
| 저장소 | PostgreSQL 또는 MariaDB |
| 파일 저장 | NAS, S3 호환 스토리지, Git 저장소 |
| 검색 | OpenSearch 또는 PostgreSQL Full Text |
| AI Context | Markdown |
| Jira 연동 | Jira Cloud REST API |
| Confluence 연동 | Confluence REST API |
| Slack 연동 | Slack Web API |
| 인증 | OAuth2, API Token, 사내 SSO |
| 배포 | Docker, Kubernetes 또는 기관 표준 WAS |

### 12.2 Maven 의존성 예시

```xml
<dependencies>
    <!-- Spring Boot -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-batch</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-quartz</artifactId>
    </dependency>

    <!-- Document parsing -->
    <dependency>
        <groupId>org.apache.tika</groupId>
        <artifactId>tika-core</artifactId>
        <version>3.2.3</version>
    </dependency>

    <dependency>
        <groupId>org.apache.tika</groupId>
        <artifactId>tika-parsers-standard-package</artifactId>
        <version>3.2.3</version>
    </dependency>

    <dependency>
        <groupId>org.apache.poi</groupId>
        <artifactId>poi-ooxml</artifactId>
        <version>5.4.1</version>
    </dependency>

    <!-- Markdown / HTML utility -->
    <dependency>
        <groupId>org.jsoup</groupId>
        <artifactId>jsoup</artifactId>
        <version>1.18.3</version>
    </dependency>

    <!-- HTTP clients for Jira, Confluence, Slack -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-webflux</artifactId>
    </dependency>
</dependencies>
```

---

## 13. 핵심 Java 인터페이스 설계

### 13.1 공통 Converter 인터페이스

```java
public interface DocumentToMarkdownConverter {

    boolean supports(String extension, String contentType);

    MarkdownDocument convert(DocumentSource source, InputStream inputStream);
}
```

### 13.2 Word 변환기 예시

```java
@Component
public class WordToMarkdownConverter implements DocumentToMarkdownConverter {

    private final Tika tika = new Tika();

    @Override
    public boolean supports(String extension, String contentType) {
        return extension.equalsIgnoreCase("doc")
            || extension.equalsIgnoreCase("docx");
    }

    @Override
    public MarkdownDocument convert(DocumentSource source, InputStream inputStream) {
        try {
            String text = tika.parseToString(inputStream);

            String markdown = """
                ---
                source_file: %s
                document_type: word
                ---

                # %s

                %s
                """.formatted(
                    source.getFileName(),
                    removeExtension(source.getFileName()),
                    normalizeText(text)
                );

            return MarkdownDocument.of(source, markdown);
        } catch (Exception e) {
            throw new DocumentConvertException("Word 문서 변환 실패: " + source.getFileName(), e);
        }
    }

    private String normalizeText(String text) {
        return text
            .replace("\r\n", "\n")
            .replaceAll("\n{3,}", "\n\n");
    }

    private String removeExtension(String fileName) {
        int index = fileName.lastIndexOf(".");
        return index > 0 ? fileName.substring(0, index) : fileName;
    }
}
```

### 13.3 Excel 변환기 예시

```java
@Component
public class ExcelToMarkdownConverter implements DocumentToMarkdownConverter {

    @Override
    public boolean supports(String extension, String contentType) {
        return extension.equalsIgnoreCase("xls")
            || extension.equalsIgnoreCase("xlsx");
    }

    @Override
    public MarkdownDocument convert(DocumentSource source, InputStream inputStream) {
        try (Workbook workbook = WorkbookFactory.create(inputStream)) {
            StringBuilder md = new StringBuilder();

            md.append("---\n");
            md.append("source_file: ").append(source.getFileName()).append("\n");
            md.append("document_type: spreadsheet\n");
            md.append("---\n\n");
            md.append("# ").append(source.getFileName()).append("\n\n");

            for (int i = 0; i < workbook.getNumberOfSheets(); i++) {
                Sheet sheet = workbook.getSheetAt(i);
                md.append("## Sheet: ").append(sheet.getSheetName()).append("\n\n");
                appendSheetAsMarkdownTable(sheet, md);
                md.append("\n");
            }

            return MarkdownDocument.of(source, md.toString());
        } catch (Exception e) {
            throw new DocumentConvertException("Excel 문서 변환 실패: " + source.getFileName(), e);
        }
    }

    private void appendSheetAsMarkdownTable(Sheet sheet, StringBuilder md) {
        int firstRow = sheet.getFirstRowNum();
        int lastRow = sheet.getLastRowNum();

        for (int rowIndex = firstRow; rowIndex <= lastRow; rowIndex++) {
            Row row = sheet.getRow(rowIndex);
            if (row == null) continue;

            List<String> cells = new ArrayList<>();
            for (int cellIndex = 0; cellIndex < row.getLastCellNum(); cellIndex++) {
                Cell cell = row.getCell(cellIndex, Row.MissingCellPolicy.CREATE_NULL_AS_BLANK);
                cells.add(escapeMarkdown(getCellValue(cell)));
            }

            md.append("| ").append(String.join(" | ", cells)).append(" |\n");

            if (rowIndex == firstRow) {
                md.append("| ");
                md.append(cells.stream().map(c -> "---").collect(Collectors.joining(" | ")));
                md.append(" |\n");
            }
        }
    }

    private String getCellValue(Cell cell) {
        return switch (cell.getCellType()) {
            case STRING -> cell.getStringCellValue();
            case NUMERIC -> DateUtil.isCellDateFormatted(cell)
                ? cell.getLocalDateTimeCellValue().toString()
                : BigDecimal.valueOf(cell.getNumericCellValue()).stripTrailingZeros().toPlainString();
            case BOOLEAN -> Boolean.toString(cell.getBooleanCellValue());
            case FORMULA -> cell.getCellFormula();
            case BLANK -> "";
            default -> "";
        };
    }

    private String escapeMarkdown(String value) {
        return value == null ? "" : value.replace("|", "\\|").replace("\n", "<br>");
    }
}
```

### 13.4 PowerPoint 변환기 예시

```java
@Component
public class PowerPointToMarkdownConverter implements DocumentToMarkdownConverter {

    @Override
    public boolean supports(String extension, String contentType) {
        return extension.equalsIgnoreCase("ppt")
            || extension.equalsIgnoreCase("pptx");
    }

    @Override
    public MarkdownDocument convert(DocumentSource source, InputStream inputStream) {
        try (XMLSlideShow ppt = new XMLSlideShow(inputStream)) {
            StringBuilder md = new StringBuilder();

            md.append("---\n");
            md.append("source_file: ").append(source.getFileName()).append("\n");
            md.append("document_type: presentation\n");
            md.append("---\n\n");
            md.append("# ").append(source.getFileName()).append("\n\n");

            int slideNo = 1;
            for (XSLFSlide slide : ppt.getSlides()) {
                md.append("## Slide ").append(slideNo++).append("\n\n");

                for (XSLFShape shape : slide.getShapes()) {
                    if (shape instanceof XSLFTextShape textShape) {
                        String text = textShape.getText();
                        if (text != null && !text.isBlank()) {
                            md.append(text.trim()).append("\n\n");
                        }
                    }
                }
            }

            return MarkdownDocument.of(source, md.toString());
        } catch (Exception e) {
            throw new DocumentConvertException("PowerPoint 문서 변환 실패: " + source.getFileName(), e);
        }
    }
}
```

### 13.5 HWPX 변환기 초안

```java
@Component
public class HwpxToMarkdownConverter implements DocumentToMarkdownConverter {

    @Override
    public boolean supports(String extension, String contentType) {
        return extension.equalsIgnoreCase("hwpx");
    }

    @Override
    public MarkdownDocument convert(DocumentSource source, InputStream inputStream) {
        try (ZipInputStream zis = new ZipInputStream(inputStream)) {
            StringBuilder md = new StringBuilder();

            md.append("---\n");
            md.append("source_file: ").append(source.getFileName()).append("\n");
            md.append("document_type: hwpx\n");
            md.append("---\n\n");
            md.append("# ").append(source.getFileName()).append("\n\n");

            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                if (entry.getName().endsWith(".xml")
                    && entry.getName().toLowerCase().contains("section")) {

                    String xml = new String(zis.readAllBytes(), StandardCharsets.UTF_8);
                    String text = extractTextFromXml(xml);

                    if (!text.isBlank()) {
                        md.append("## ").append(entry.getName()).append("\n\n");
                        md.append(text).append("\n\n");
                    }
                }
            }

            return MarkdownDocument.of(source, md.toString());
        } catch (Exception e) {
            throw new DocumentConvertException("HWPX 문서 변환 실패: " + source.getFileName(), e);
        }
    }

    private String extractTextFromXml(String xml) {
        Document document = Jsoup.parse(xml, "", Parser.xmlParser());

        return document.select("*").stream()
            .filter(element -> element.ownText() != null && !element.ownText().isBlank())
            .map(element -> element.ownText().trim())
            .distinct()
            .collect(Collectors.joining("\n\n"));
    }
}
```

---

## 14. Claude Context 생성 규칙

변환된 Markdown 전체를 그대로 전달하지 않고, Jira 단계별로 필요한 문서만 묶어 Claude용 Context를 생성한다.

### 14.1 요구사항 확인 단계 Context

```markdown
# Claude Context: 요구사항 확인

## 관련 Jira

- GOV-123 민원 신청 기능 개발

## 참조 문서

- 요구사항정의서.md
- 고객인터뷰회의록.md
- 요구사항추적표.md

## 요구사항 요약

...

## 확인 필요사항

...

## 개발 전 질문

...
```

### 14.2 개발 단계 Context

```markdown
# Claude Context: 개발

## 구현 대상

- REQ-FN-001 민원 신청서 작성

## 관련 설계

- 화면설계서 SCR-001
- API-001 신청서 저장 API
- DB 테이블 TB_APPLICATION

## 구현 규칙

- Controller에는 비즈니스 로직 작성 금지
- Service에서 트랜잭션 처리
- Mapper는 데이터 접근만 담당
- 공통 응답 포맷 사용
- 공통 예외 처리 사용

## 참조 문서

...
```

### 14.3 테스트 단계 Context

```markdown
# Claude Context: 테스트

## 테스트 대상 요구사항

| 요구사항 ID | 테스트케이스 |
|---|---|
| REQ-FN-001 | TC-001, TC-002 |

## 테스트 시나리오

...

## 결함 확인 기준

...
```

---

## 15. Jira 연동 설계

### 15.1 Jira Webhook 이벤트

| 이벤트 | 처리 |
|---|---|
| Issue Created | 관련 문서 검색 및 Context 초안 생성 |
| Issue Updated | 상태 변경 감지 |
| Status = 요구사항 확인 | 요구사항 문서 Context 생성 |
| Status = 개발중 | 설계/개발 Context 생성 |
| Status = 테스트중 | 테스트 Context 생성 |
| Status = 통합테스트중 | 통합테스트 Context 생성 |
| Status = 배포대기 | 배포 체크리스트 Context 생성 |

### 15.2 Jira 이슈 필드 권장

| 필드 | 설명 |
|---|---|
| Requirement ID | `REQ-FN-001` |
| Document Links | Confluence 문서 링크 |
| Source Document | 원본 문서명 |
| Markdown Context | 변환된 Markdown 링크 |
| Phase | 요구사항 / 개발 / 테스트 / 통합테스트 / 배포 |
| Claude Context | Claude용 Context 파일 링크 |

---

## 16. REST API 설계

### 16.1 문서 업로드

```http
POST /api/documents/upload
Content-Type: multipart/form-data
```

### 16.2 문서 변환

```http
POST /api/documents/{documentId}/convert
```

### 16.3 Jira 이슈 기준 Context 생성

```http
POST /api/jira/issues/{issueKey}/context
```

### 16.4 단계별 Context 조회

```http
GET /api/jira/issues/{issueKey}/context?phase=DEVELOPMENT
```

### 16.5 Confluence 동기화

```http
POST /api/confluence/sync
```

### 16.6 Slack 알림 재전송

```http
POST /api/slack/notify
```

---

## 17. 배치 / 스케줄러 설계

### 17.1 정기 동기화

```text
매 10분:
- Jira 변경 이슈 조회
- Confluence 변경 문서 조회
- 변경 문서 Markdown 재변환
- 관련 Jira 이슈 Context 갱신
```

### 17.2 단계 변경 감지

```text
Jira Status 변경:
- 요구사항 확인 → 요구사항 Context 생성
- 개발중 → 개발 Context 생성
- 테스트중 → 테스트 Context 생성
- 통합테스트중 → 통합테스트 Context 생성
- 배포대기 → 배포 Context 생성
```

---

## 18. 보안 설계

정부기관 프로젝트에서는 문서와 AI 활용 보안이 중요하다.

| 항목 | 설계 |
|---|---|
| 원본 문서 보관 | 내부 저장소 또는 암호화 스토리지 |
| 개인정보 탐지 | 주민번호, 전화번호, 이메일, 주소 패턴 마스킹 |
| API Key | Vault, Secret Manager, 환경변수 사용 |
| 권한 | Jira/Confluence 권한과 연동 |
| 로그 | 문서 전문 출력 금지 |
| AI 전달 | 필요한 Markdown Context만 전달 |
| 이력 | 누가, 언제, 어떤 문서를 변환했는지 감사 로그 저장 |
| 반출통제 | 외부 LLM 전송 전 승인 단계 선택 가능 |

---

## 19. MVP 범위

### 19.1 1차 MVP

```text
- Confluence 첨부파일 수집
- 로컬 폴더 문서 수집
- docx, xlsx, pptx, hwpx Markdown 변환
- Jira 이슈 키 기준 문서 매핑
- 단계별 Claude Context 생성
- Slack 알림
```

### 19.2 2차 확장

```text
- doc, xls, ppt 구버전 지원 강화
- 표/이미지/도형 추출 고도화
- 요구사항 ID 자동 추출
- 테스트케이스 자동 생성
- Confluence 페이지 자동 업데이트
- Jira 이슈 자동 생성
```

### 19.3 3차 확장

```text
- Claude API 또는 Claude Code 연계
- 벡터 검색/RAG 구성
- 문서 변경 영향도 분석
- 요구사항-코드-테스트 추적 자동화
- 배포 체크리스트 자동 생성
```

---

## 20. 개발 우선순위

가장 먼저 구현할 핵심 기능은 다음 5개다.

```text
1. Document Collector
2. DocumentToMarkdownConverter
3. Jira Phase Watcher
4. Claude Context Builder
5. Slack Notifier
```

---

## 21. 결론

Doc2Claude Manager는 단순 문서 변환기가 아니라 **프로젝트 산출물 자동 이해·추적 시스템**으로 설계해야 한다.

핵심 구조는 다음과 같다.

```text
문서 수집
→ Markdown 변환
→ 요구사항/설계/테스트 정보 추출
→ Jira 일정 상태와 연결
→ Claude용 Context 생성
→ Confluence 저장
→ Slack 알림
→ 개발/테스트/배포 단계에서 자동 참조
```

이 구조로 만들면 정부기관 프로젝트 산출물인 요구사항정의서, 회의록, 화면설계서, API설계서, 테스트결과서, 배포계획서를 Claude가 이해 가능한 Markdown으로 자동 정리하고, Jira 일정 상태에 따라 개발·테스트·배포 작업에 바로 활용할 수 있다.
