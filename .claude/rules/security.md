# Security Rules — egov-demo

> 전자정부표준프레임워크 Java/Spring/MyBatis 보안 체크리스트

---

## SQL Injection 방지

### ✅ Good: 파라미터 바인딩

```xml
<select id="selectList">
    SELECT SAMPLE_ID, SAMPLE_NM, REG_USR_ID, FRST_REGIST_PNTTM
    FROM SAMPLE_TBL
    WHERE 1=1
    <if test="searchKeyword != null and searchKeyword != ''">
        AND SAMPLE_NM LIKE '%' || #{searchKeyword} || '%'
    </if>
    ORDER BY FRST_REGIST_PNTTM DESC
</select>
```

### ❌ Bad: 사용자 입력값 직접 치환

```xml
<!-- 금지: SQL Injection 위험 -->
<select id="selectList">
    SELECT * FROM SAMPLE_TBL
    WHERE SAMPLE_NM = '${searchKeyword}'
</select>
```

### ORDER BY 예외

동적 ORDER BY가 필요한 경우, 화이트리스트 검증 후 `${}` 사용:

```java
// Controller에서 검증
if (!Arrays.asList("FRST_REGIST_PNTTM", "SAMPLE_NM").contains(orderBy)) {
    orderBy = "FRST_REGIST_PNTTM";  // 기본값
}
vo.setOrderBy(orderBy);  // Mapper에서 ${orderBy} 사용 가능
```

---

## XSS 방지

### ✅ Good: JSP에서 이스케이프

```jsp
<!-- Good: 자동 이스케이프 -->
<c:out value="${searchKeyword}"/>

<!-- Good: 속성값 이스케이프 -->
<input type="text" value="<c:out value='${vo.sampleName}'/>">
```

### ❌ Bad: 이스케이프 없음

```jsp
<!-- 금지: XSS 위험 -->
${searchKeyword}

<!-- 금지: 속성값 노출 -->
<input type="text" value="${vo.sampleName}">
```

### Spring Security XSS 필터

`web.xml`에서 설정:

```xml
<filter>
    <filter-name>xssFilter</filter-name>
    <filter-class>org.springframework.security.web.header.writers.XContentTypeOptionsHeaderWriter</filter-class>
</filter>
```

---

## 인증·인가 확인

### ✅ 로그인 필수 메서드

```java
@PostMapping("/example/sample/insertSample.do")
public String insertSample(SampleVO vo, Model model) {
    // 인증 확인
    LoginVO loginVO = (LoginVO) EgovUserDetailsHelper.getAuthenticatedUser();
    if (loginVO == null) {
        return "redirect:/uat/uia/egovLoginUsr.do";
    }
    
    // 관리자 권한 확인
    if (!EgovUserDetailsHelper.isAdmin()) {
        throw new EgovBizException("관리자만 등록 가능합니다.");
    }
    
    vo.setRegUsrId(loginVO.getUserId());
    sampleService.insertSample(vo);
    
    return "redirect:/example/sample/selectList.do";
}
```

---

## 비밀정보 관리

### ❌ 금지

```java
// 금지: 하드코딩
private static final String DB_PASSWORD = "admin123";

// 금지: 로깅
logger.info("User password: " + password);

// 금지: 커밋
.env 파일 커밋
secrets.properties 커밋
```

### ✅ 올바른 방식

```properties
# globals.properties (비로그인 필요)
db.password=${DB_PASSWORD}  # 환경변수로 대체

# Java 코드
String dbPassword = env.getProperty("db.password");
if (dbPassword == null) {
    throw new RuntimeException("DB_PASSWORD 환경변수 필수");
}
```

### .gitignore

```
*.env
**/secrets.properties
**/config.properties
**/*-local.properties
.DS_Store
target/
```

---

## 파일 업로드 보안

### ✅ Good: 확장자 화이트리스트

```java
public String uploadFile(MultipartFile file) {
    String filename = file.getOriginalFilename();
    String extension = filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
    
    // 허용 확장자
    List<String> allowedExtensions = Arrays.asList("pdf", "doc", "docx", "xlsx");
    if (!allowedExtensions.contains(extension)) {
        throw new EgovBizException("PDF, DOC, DOCX, XLSX 파일만 업로드 가능합니다.");
    }
    
    // 경로는 항상 서버 지정 경로 사용
    String uploadPath = "/uploads/" + UUID.randomUUID();
    return EgovFileUploadUtil.uploadFile(file, uploadPath);
}
```

### ❌ 금지

```java
// 금지: 사용자 입력 경로 사용
String uploadPath = request.getParameter("path");  // 경로 조작 위험

// 금지: 확장자 검증 없음
file.transferTo(new File("/uploads/" + file.getOriginalFilename()));
```

---

## 에러 메시지

### ✅ Good: 최소 정보만 노출

```java
try {
    return sampleDAO.selectList(vo);
} catch (Exception e) {
    // 사용자에게는 최소 정보만
    throw new EgovBizException("조회 중 오류가 발생했습니다.");
    // 상세 정보는 로그에만 기록
    // logger.error("Database error: {}", e.getMessage(), e);
}
```

### ❌ Bad: 내부 정보 노출

```java
// 금지: 데이터베이스 정보 노출
throw new Exception("Database connection failed: jdbc:oracle:thin:@localhost:1521");

// 금지: 스택 트레이스 노출
e.printStackTrace();
```

---

## 보안 체크리스트 (제출 전)

- [ ] Mapper XML에 `${}` 사용 여부 확인 (ORDER BY 외 금지)
- [ ] JSP 출력값 `<c:out>` 이스케이프 확인
- [ ] 인증 필요 Controller 세션 확인 로직 확인
- [ ] 파일 업로드 확장자 검증 확인
- [ ] 에러 메시지에 내부 정보 노출 안 함 확인
- [ ] 비밀정보 하드코딩 검색 → 0건
- [ ] .env, secrets.properties 파일 .gitignore 추가 확인
- [ ] 암호화 저장 (BCrypt, PBKDF2) 확인
- [ ] SQL LIKE 검색어 특수문자 이스케이프 확인
