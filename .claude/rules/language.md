# Language Rules — egov-demo

> 코드·로그는 영어, 사용자 응답은 한국어

---

## 사용자 응답

- **항상 한국어로 응답한다.**
- 설명, 질문, 상태 업데이트 모두 한국어 사용.

---

## Java 코드

전자정부프레임워크 네이밍 표준:

| 구분 | 규칙 | 예시 |
|---|---|---|
| 클래스명 | PascalCase (영문) | `EgovSampleController` |
| 메서드명 | camelCase (영문) | `selectList`, `insertSample` |
| 변수명 | camelCase (영문) | `searchVO`, `resultMap` |
| 상수 | UPPER_SNAKE_CASE (영문) | `PAGE_SIZE`, `MAX_RETRIES` |
| 테스트 메서드 | camelCase + 한글 설명 | `selectList_검색어없으면_전체목록반환한다` |

**예:**
```java
public class EgovSampleController {
    private static final int PAGE_SIZE = 10;
    
    public Map<String, Object> selectList(SampleVO searchVO) {
        List<SampleVO> resultList = sampleService.selectList(searchVO);
        Map<String, Object> resultMap = new HashMap<>();
        resultMap.put("resultList", resultList);
        return resultMap;
    }
}
```

---

## SQL (Oracle)

- **SQL 키워드**: 대문자
- **컬럼명**: 언더스코어 대문자 (Oracle 표준)
- **주석**: 한국어 허용

**예:**
```sql
-- 샘플 목록 조회 (페이징)
SELECT * FROM (
    SELECT ROWNUM RN, A.* FROM (
        SELECT SAMPLE_ID, SAMPLE_NM, REG_USR_ID, FRST_REGIST_PNTTM
        FROM SAMPLE_TBL
        WHERE 1=1
        AND SAMPLE_NM LIKE '%' || ? || '%'  -- 검색어
        ORDER BY FRST_REGIST_PNTTM DESC
    ) A WHERE ROWNUM <= ?  -- 마지막 인덱스
) WHERE RN > ?  -- 시작 인덱스
```

---

## MyBatis Mapper XML

```xml
<mapper namespace="egovframework.example.sample.SampleDAO">

    <!-- 샘플 목록 조회 -->
    <select id="selectList" resultType="egovframework.example.sample.SampleVO">
        SELECT * FROM (
            SELECT ROWNUM RN, A.* FROM (
                SELECT SAMPLE_ID, SAMPLE_NM FROM SAMPLE_TBL
                <where>
                    <if test="searchKeyword != null and searchKeyword != ''">
                        AND SAMPLE_NM LIKE '%' || #{searchKeyword} || '%'
                    </if>
                </where>
                ORDER BY FRST_REGIST_PNTTM DESC
            ) A WHERE ROWNUM <![CDATA[<=]]> #{lastIndex}
        ) WHERE RN <![CDATA[>]]> #{firstIndex}
    </select>
</mapper>
```

---

## JSP

```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>

<h1>샘플 목록</h1>

<!-- 검색 조건 -->
<form method="post" action="/example/sample/selectList.do">
    <input type="text" name="searchKeyword" value="<c:out value='${searchVO.searchKeyword}'/>">
    <button type="submit">검색</button>
</form>

<!-- 목록 테이블 -->
<table>
    <thead>
        <tr>
            <th>샘플 ID</th>
            <th>샘플명</th>
            <th>등록자</th>
            <th>등록일</th>
        </tr>
    </thead>
    <tbody>
        <c:forEach var="sample" items="${resultList}">
            <tr>
                <td><c:out value="${sample.sampleId}"/></td>
                <td><c:out value="${sample.sampleName}"/></td>
                <td><c:out value="${sample.regUsrId}"/></td>
                <td><fmt:formatDate value="${sample.frstRegistPnttm}" pattern="yyyy-MM-dd"/></td>
            </tr>
        </c:forEach>
    </tbody>
</table>
```

---

## 주석 및 Javadoc

- **소스 주석**: 한국어 허용
- **Javadoc**: 영문 권장 (API 문서용)
- **테스트 메서드명**: 한글 (설명적 메서드명)

```java
/**
 * 샘플 목록을 조회한다.
 * 
 * @param searchVO 검색 조건
 * @return 샘플 목록 (페이징 포함)
 */
public Map<String, Object> selectList(SampleVO searchVO) {
    // 검색 조건 유효성 검증
    if (searchVO == null) {
        throw new IllegalArgumentException("검색 조건이 필수입니다.");
    }
    
    return sampleDAO.selectList(searchVO);  // DAO 호출
}
```

---

## Git 커밋 메시지

한국어 또는 영문 모두 허용:

```bash
# 영문
git commit -m "feat: Add sample list functionality with pagination"

# 한국어
git commit -m "feat: 샘플 목록 조회 기능 추가 (페이징 포함)"
```

권장: 타입(feat/fix/refactor/test/docs) + 한국어 설명

---

## CLAUDE.md, AGENTS.md, 규칙 문서

- **한국어로 작성한다.**
- 기술적 정확성이 우선.

