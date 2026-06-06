# Development Environment — egov-demo

> 전자정부표준프레임워크 Java + Maven + Oracle 11g 개발 환경

---

## 빌드 도구: Maven

### 기본 명령어

```bash
# 컴파일 확인 (가장 빠름)
mvn -q -DskipTests compile

# 전체 테스트 실행
mvn -q test

# WAR 패키지 빌드
mvn -q -DskipTests package

# 캐시 정리 후 재빌드
mvn -q clean && mvn -q -DskipTests compile

# 특정 테스트만 실행
mvn -q test -Dtest=SampleControllerTest
mvn -q test -Dtest=SampleDAOTest
```

### pom.xml 표준

```xml
<groupId>egovframework.com</groupId>
<artifactId>egov-demo</artifactId>
<version>1.0.0</version>
<packaging>war</packaging>

<parent>
    <groupId>org.egovframe.web</groupId>
    <artifactId>egovframe-web-config-parent</artifactId>
    <version>5.0.0</version>
</parent>

<properties>
    <java.version>17</java.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

---

## Oracle 11g Database (Docker)

### 상태 확인

```bash
# 컨테이너 실행 확인
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'

# 포트 연결 확인
nc -zv localhost 1521

# 접속 정보
# 파일: src/main/resources/egovframework/egovProps/globals.properties
# Url: jdbc:oracle:thin:@localhost:1521:XE
# User: EGOV
# Password: {설정된 비밀번호}
```

### Docker Compose (템플릿)

```yaml
version: '3.8'

services:
  oracle:
    image: wnameless/oracle-xe-11g-r2
    ports:
      - "1521:1521"
    environment:
      - ORACLE_ALLOW_REMOTE: 'true'
    volumes:
      - oracle_data:/u01/app/oracle
    healthcheck:
      test: ["CMD", "sqlplus", "-L", "EGOV/egov@localhost:1521/XE"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  oracle_data:
```

---

## 프로젝트 구조

```
egov-demo/
├── src/main/
│   ├── java/egovframework/example/
│   │   ├── <domain>/
│   │   │   ├── service/        # Service 인터페이스 + VO
│   │   │   ├── serviceImpl/     # ServiceImpl
│   │   │   └── web/            # Controller
│   │   └── common/             # 공통 클래스
│   │
│   ├── resources/egovframework/
│   │   ├── spring/             # Spring 설정 (context-*.xml)
│   │   ├── sqlmap/example/     # MyBatis Mapper XML
│   │   └── egovProps/          # 환경 설정 (globals.properties)
│   │
│   └── webapp/WEB-INF/
│       ├── jsp/egov/           # JSP 뷰 (Egov prefix)
│       └── web.xml             # 디스패처 서블릿 설정
│
└── src/test/
    └── java/egovframework/     # JUnit 테스트
        ├── web/                # Controller 테스트
        ├── service/            # Service 테스트
        └── service/impl/       # DAO 테스트
```

### Mapper XML 위치 규칙

```bash
src/main/resources/egovframework/sqlmap/example/<domain>/
└── <Domain>Mapper.xml

# 예: SampleMapper.xml
```

### JSP 위치 규칙

```bash
src/main/webapp/WEB-INF/jsp/egov/<domain>/
├── Egov<Domain>List.jsp
├── Egov<Domain>Regist.jsp
└── Egov<Domain>Detail.jsp

# 예:
# EgovSampleList.jsp
# EgovSampleRegist.jsp
# EgovSampleDetail.jsp
```

---

## 테스트 실행

### Controller 테스트

```bash
mvn -q test -Dtest=EgovSampleControllerTest
```

테스트는 `src/test/java/egovframework/example/sample/web/` 위치.

### Service 테스트

```bash
mvn -q test -Dtest=EgovSampleServiceTest
```

테스트는 `src/test/java/egovframework/example/sample/service/` 위치.

### DAO 테스트 (Oracle 실DB)

```bash
mvn -q test -Dtest=SampleDAOTest
```

**필수:** `@Transactional + rollback` 으로 DB 원상복구.

---

## Git 상태 확인

```bash
# 변경 파일 확인
git status

# 변경 내용 확인
git diff --stat

# 커밋 이력 확인
git log --oneline -10
```

---

## 완료 검증 (필수)

모든 작업 완료 전에 다음을 반드시 실행:

```bash
# 1. 컴파일 확인
mvn -q -DskipTests compile
# → 컴파일 에러 없음

# 2. 테스트 실행
mvn -q test
# → 모든 테스트 통과, 실패 0건

# 3. 패키지 빌드
mvn -q -DskipTests package
# → target/egov-demo-1.0.0.war 생성됨

# 4. Oracle 상태 확인
docker ps | grep oracle
nc -zv localhost 1521
# → Oracle 11g 컨테이너 실행 중
```

---

## 문제 해결

### Maven 캐시 문제

```bash
rm -rf .m2/repository/{egovframework,org}
mvn -q clean && mvn -q -DskipTests compile
```

### 테스트 실패

```bash
# 단일 테스트 상세 로그
mvn test -Dtest=SampleDAOTest -X

# Oracle 연결 확인
nc -zv localhost 1521

# 데이터베이스 상태 재확인
docker ps | grep oracle
```

### 패키지 빌드 실패

```bash
# 이전 빌드 산출물 정리
mvn -q clean

# 캐시 재설정
rm -rf target .m2

# 재빌드
mvn -q -DskipTests package
```

