---
marp: true
theme: gaia
style: |
  section {
    background-color: #f5f5f5;
    color: #333;
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }
  h1 {
    font-size: 1.5em;
  }
  h2 {
    font-size: 1.2em;
  }
  h3 {
    font-size: 1.0em;
  }
  h4 {
    font-size: 0.8em;
  }
  h5 {
    font-size: 0.6em;
  }
  h6 {
    font-size: 0.4em;
  }
  p, li, table, code, pre, blockquote, textarea {
    font-size: 0.6em;
  }
---
# AI 협업도구 기반 전자정부 표준프레임워크 프로젝트 관리 혁신

### — 클로드 하네스(Claude Harness)를 활용한 SI 수행 최적화 방안 —

> ※ 본 보고서에 표기된 정량 수치(투입시간, 비용, KPI 등)는 공공 SI 사업의 통상 범위를 기준으로 한 **예시값**이며, 직전 사업 실적 확보 후 확정한다.

---

## 0. Executive Summary

공공기관 SI 프로젝트는 전체 공정의 상당 비중이 **산출물 작성·검토·취합**과 **요구사항 추적관리**에 투입되며, 이 영역의 비효율이 공정 지연·품질 저하·감리 리스크로 이어진다. 본 과제는 Jira·Confluence·Slack·Claude 등 AI 협업도구를 활용해 이 공정을 표준화·자동화하는 업무 혁신 방안이다.

| 구분 | 내용 |
| --- | --- |
| **현재 문제** | ① 산출물 취합·보고서 작성이 수작업 중심 (주간보고 1건당 약 4시간 소요) |
| | ② 요구사항 추적성이 개발·테스트 단계에서 단절되어 감리 시 재정리 부담 |
| | ③ 개발자 주관 보고로 공정률이 왜곡, 오픈 시점 결함 집중 |
| **제안** | AI 협업도구로 문서·요구사항·공정·개발·감리 대응을 표준화·자동화 |
| **기대효과(예시)** | DA에이전트 기준 요구사항기반확정 시 데이터 모델링, 표준화, 테이블생성 10~20분으로 단축 |
| **필요 의사결정** | ① AI 도구 사용 승인 ② 시범적용 4개 업무 승인 ③ figma UI/UX 컴포넌트 작성 지원 |
| **소요(예시)** | 1차년도 PM, DA, egov-dev, tdd, deploye 에이전트별(Max 20x: 월 $200 계정사용) / DA-agent max20X 사용시 복잡한 모델링을 5시간에 20번 수행가능 |

---

## 1. 추진 목적

공공기관 SI 프로젝트 수행 과정에서 반복적으로 발생하는 **문서 품질 저하, 요구사항 추적성 단절, 공정률 왜곡, 산출물 취합 지연, 개발 품질 저하** 문제를 개선하기 위해, Jira·Confluence·Slack·Claude 등 AI 기반 협업 도구를 활용한 프로젝트 관리 및 개발 최적화 방안과 체계를 수립하는 데 목적이 있다.

특히 공공기관 프로젝트는 전체 공정의 상당 부분이 **사업관리 및 개발 산출물 작성·검토·취합**에 집중되어 있으며, 감리·검수 단계에서 산출물 품질과 요구사항 추적성이 주요 점검 대상이 된다. 이에 따라 AI를 단순 코딩 보조 도구로 활용하는 수준을 넘어, **프로젝트 전 공정의 역할·룰·스킬을 표준화하고 자동화하는 업무 혁신 체계를 수립**하고자 한다.

---

## 2. 추진 배경

공공기관 프로젝트는 전통적으로 폭포수 모델 중심으로 운영되어 왔으며, 요구사항 정의, 분석, 설계, 개발, 테스트, 감리, 검수 단계가 순차적으로 진행된다. 그러나 실제 수행 과정에서는 다음과 같은 문제가 반복적으로 발생한다.

첫째, 산출물 작성과 취합이 수작업 중심으로 이루어져 문서 품질 확보에 많은 시간이 소요된다.
둘째, 요구사항 추적관리가 최초 작성 시점에는 이루어지지만, 개발과 테스트가 진행되면서 지속적으로 유지되지 않는다.
셋째, 주간보고와 월간보고 작성 시 WBS, 이슈, 산출물, 결함, 개발 진행률을 별도 담당자가 수작업으로 취합하고 있다.
넷째, 요구사항이 불명확하거나 테스트 기준이 부족한 상태에서 개발이 진행되면 오픈 시점에 다수의 오류가 발생하고, 이후 긴급 수정과 재작업 비용이 증가한다.
다섯째, 공공기관 특성상 폭포수 방식이 강하게 적용되어 개발 완료 후 품질 문제가 집중적으로 드러나는 구조가 발생한다.

#### [표 2-1] 현황 문제와 개선 전 기준선(baseline, 예시)

| 문제 영역 | 현재 수준(예시) | 비고 |
| --- | --- | --- |
| 주간보고 작성 | 1건당 약 4시간 | 담당자 수작업 취합 |
| 요구사항 추적 누락률 | 약 15% | 감리 지적 주요 원인 |
| 오픈 후 결함 | 직전 사업 기준 다수 발생 | 폭포수 후행 테스트 |
| 산출물 검토 리드타임 | 평균 2~3일 | 개별 검토 의견 관리 |

---

## 3. 추진 방향

본 프로젝트 관리 최적화의 핵심 방향은 다음과 같다.

```text
문서관리 자동화 → 요구사항 추적관리 자동화 → 공정관리 자동화 → SDD + TDD 기반 요구사항 작성
→ AI 기반 역할·룰·스킬 정착 → 전자정부 표준프레임워크 최적화 개발 → 배포 → 통합테스트 → 산출물 작성
```
[그림 3-1] 추진 방향 흐름도

이를 위해 Jira, Confluence, Slack, Claude를 기본 협업 도구로 활용하고, 필요 시 AI CLI 도구를 도입하여 프로젝트 관리와 개발 수행 전반에 AI 자동화 체계를 적용한다.

---

## 4. 주요 개선 목표
### 4.1 문서 품질 확보
정부기관 프로젝트는 사업관리 및 개발 산출물 관리 비중이 높으며, 산출물 품질은 감리·검수 대응의 핵심 요소이다.

#### [표 4-1] 문서관리 개선 방향

| 구분    | 기존 방식            | 개선 방식                                 |
| ----- | ---------------- | ------------------------------------- |
| 문서 작성 | 담당자별 개별 작성       | Confluence 표준 템플릿 기반 작성               |
| 문서 취합 | PM/문서 담당자 수작업 취합 | Jira/Confluence 기반 자동 취합              |
| 문서 검토 | 개별 검토 의견 관리      | Claude 기반 누락/불일치 검토                   |
| 버전 관리 | 파일명 중심 관리        | Confluence Page + Attachment + 기준선 관리 |
| 보고 자료 | 수작업 복사/정리        | 자동 보고서 초안 생성                          |

기대 효과는 산출물 취합 및 검토 시간을 단축하고, 감리·검수 단계에서 문서 품질 관련 리스크를 사전에 줄이는 것이다.

---

### 4.2 요구사항 추적관리 강화

공공기관 프로젝트에서는 요구사항 ID를 기준으로 유스케이스, 화면, API, 프로그램, 테이블, 테스트케이스까지 추적해야 한다. 단계별 산출물 간 ID 연결이 유지되지 않아 감리 시 많은 시간을 소요한다.

개선 방향은 다음과 같다.
```text
요구사항추적표를 기준으로 Jira 필드에 다음 사항을 추가하여 집중관리한다.
요구사항 ID → 유스케이스 ID → 화면 ID → API ID → 프로그램 ID → 테이블 ID → 테스트케이스 ID → 결함 ID → 검수 승인 ID
```
[그림 4-1] 요구사항 추적 ID 체인

AI를 활용하여 기존 문서의 요구사항 ID 연결 상태를 자동 점검하고, 누락되거나 불일치한 항목을 식별하여 Jira와 Confluence 문서에 자동 업데이트한다.

#### [표 4-2] 요구사항 추적관리 개선 항목

| 관리 항목   | 개선 내용                            |
| ------- | -------------------------------- |
| 요구사항 누락 | Claude가 요구사항정의서와 유스케이스정의서 비교     |
| ID 불일치  | 문서 간 요구사항 ID, 테스트케이스 ID 연결 점검    |
| 변경 반영   | 변경된 요구사항을 관련 설계·테스트 문서에 반영       |
| 감리 대응   | 요구사항 추적표 자동 생성 및 최신화             |
| 보완 요청   | Jira Sub-task 또는 댓글로 담당자에게 보완 요청 |

이를 통해 감리 지적 가능성을 줄이고, 요구사항 변경에 따른 설계·개발·테스트 영향도를 체계적으로 관리할 수 있다.

---

### 4.3 공정관리 자동화

현재 주간보고, 월간보고 작성 시 WBS, Jira 이슈, 산출물 현황, 개발 진행률, 결함 현황을 별도 담당자가 수작업으로 취합하고 있다. 이 과정은 반복적이고 시간이 많이 소요되며, 개발자의 주관적 보고에 따라 공정률이 왜곡될 수 있다.

개선 방향은 기존의 "개발자 보고 기반 공정률"을 **"테스트 통과 기반 공정률"**로 전환하는 것이다. TDD는 이를 뒷받침하는 하위 수단으로 위치시킨다.

#### [표 4-3] 공정률 산정 기준 전환

| 기존 공정률 기준      | 개선 공정률 기준                        |
| -------------- | -------------------------------- |
| 개발자 주관적 진행률 입력 | Jira Task 완료 상태 기반 집계            |
| PM 수작업 취합      | Jira 자동 집계                       |
| 산출물 별도 확인      | Confluence Page Properties 기반 취합 |
| 테스트 결과 수동 확인   | 테스트 통과 여부 기반 자동 확인              |
| 보고서 수작업 작성     | AI 기반 주간·월간보고 자동 생성              |

공정률 산정 기준 예시는 다음과 같다. 테스트 코드는 TDD 원칙에 따라 구현보다 먼저 작성(실패 확인)하고, 구현 후 통과 여부로 공정을 인정한다.

```text
요구사항 명세 완료: 10% > 설계 문서 승인: 20% > 테스트케이스 설계 완료: 30%
> 테스트 코드 작성·실패 확인: 40% > 구현 후 단위 테스트 통과: 60%
> 통합 테스트 통과: 80% > 고객 검토 및 승인: 100%
```
[그림 4-2] 테스트 통과 기반 공정률 단계

이를 통해 허위 보고 가능성을 줄이고, 실제 산출물과 테스트 결과에 기반한 객관적 공정관리가 가능해진다.

---

### 4.4 개발 자동화 및 품질 향상

정확한 요구사항 명세를 입력으로 사용하여 Claude Code,  AI CLI 도구를 통해 기능 구현과 테스트를 자동화한다. 개발 자동화의 핵심은 단순 코드 생성이 아니라, 다음 흐름을 정착시키는 것이다.

```text
요구사항정의서 → 유스케이스정의서 → 화면정의서 → 테이블정의서 → Spec 작성 → Plan 작성
→ TDD 작성 → Task 분해 → 코드 구현 → 테스트 통과 → 산출물 업데이트
```
[그림 4-3] SDD+TDD 기반 개발 흐름

이를 통해 개발자는 반복적인 보일러플레이트 코드 작성보다 요구사항 검증, 예외 처리, 품질 개선에 집중할 수 있다.

다만 전자정부 표준프레임워크는 레거시 기반(Spring 구버전, JSP)이 많아 단위 테스트 자동화 난이도가 높다. 이에 **TDD는 서비스·DAO 레이어에 우선 적용**하고, 화면·통합 영역은 Playwright 등 E2E 테스트로 보완하는 단계적 적용 전략을 취한다.

### 4.5 애자일 개발방식 도입·정착

공공기관 프로젝트는 폭포수 모델 기반으로 수행되는 경우가 많아 개발 후반부 또는 오픈 시점에 다수의 오류가 집중적으로 발견된다. 공공기관의 공식 산출물 체계는 유지하되, 내부 개발 프로세스는 애자일 방식으로 전환하여 품질과 대응 속도를 높인다.

#### [표 4-4] 개발방식 전환

| 기존 방식         | 개선 방식          |
| ------------- | -------------- |
| 전체 설계 후 일괄 개발 | 요구사항 단위 점진 개발  |
| 오픈 시점 오류 집중   | 프로토타입 기반 조기 검증 |
| 문서와 개발 분리     | 문서·테스트·코드 연계   |
| 테스트 후행        | TDD 기반 테스트 선행  |
| 고객 피드백 지연     | 반복 검토 및 보완     |

---

## 5. AI 기반 업무 혁신 방향

본 과제의 핵심은 AI CLI 도구를 활용해 코딩만 자동화하는 것이 아니다. 프로젝트 공정에서 발생하는 역할별 룰과 워크플로우를 정리하고, AI가 이를 수행하거나 보조할 수 있도록 체계화하는 것이다.

#### [표 5-1] 영역별 AI 활용 방안

| 영역     | AI 활용 방안                       |
| ------ | ------------------------------ |
| 문서관리   | 산출물 템플릿 생성, 누락 검토, 문서 비교       |
| 요구사항관리 | 요구사항 체계화, ID 추적, 변경 영향도 분석     |
| 공정관리   | Jira Task 기반 공정률 산정, 보고서 자동 생성 |
| 개발관리   | Spec 기반 구현 계획, TDD, 코드 생성      |
| 테스트관리  | 테스트케이스 생성, 테스트 누락 점검           |
| 감리대응   | 요구사항 추적표, 산출물 현황, 보완사항 정리      |
| 운영관리   | 이슈 요약, 장애보고서, FAQ, 조치 이력 지식화   |

---

## 6. 목표 시스템 구성
![목표 시스템 구성도: Jira·Confluence·Slack·Claude 연계 구조](시스템구성도.png)
[그림 6-1] 목표 시스템 구성도

---

## 7. 핵심 아키텍처

![핵심 아키텍처 요약: 하네스-에이전트-스킬-룰-훅-MCP 구성](summary.png)
[그림 7-1] 핵심 아키텍처 요약

---

## 8. 전자정부 표준프레임워크 특화 시스템 구성
### 8.1 사업관리

![사업관리 구성: 문서·요구사항·공정·보고 자동화 체계](사업관리.png)
[그림 8-1] 사업관리 구성도

---

### 8.2 개발공정관리

![개발공정관리 구성: SDD·TDD·테스트 통과 기반 공정 체계](개발공정관리.png)
[그림 8-2] 개발공정관리 구성도

---

## 9. 보안·망분리 대응 방안

공공기관은 망분리 지침과 보안요건이 적용되므로, AI 협업도구 도입 시 보안 검토를 선제적으로 수행한다.

#### [표 9-1] 보안 쟁점 및 대응 방안

| 보안 쟁점 | 대응 방안 |
| --- | --- |
| 외부 클라우드 LLM 사용 가부 | 업무망/인터넷망 분리 적용. 민감 산출물은 내부 처리, 일반 문서는 통제된 영역에서만 처리 |
| 학습데이터 유출 우려 | 입력 데이터 비학습(Zero Data Retention) 옵션 적용 및 계약상 명시 |
| 소스코드·DB 접근 통제 | db-readonly MCP로 읽기 전용 접근, 시크릿은 별도 보안 저장소(Vault 등)에서 관리 |
| 시크릿 노출 | before-submit-secret-check 훅으로 커밋·제출 전 자동 점검 |
| 운영 주체·책임 | MCP·Hooks는 공용 통제 서버에서 운영, 개인 로컬 임의 구성 금지 |
| 망분리 환경 대안 | 인터넷망 사용이 제한될 경우 on-prem/하이브리드 모델 도입 검토 |

본 방안의 구체적 적용 범위는 기관 보안담당 부서와 협의하여 확정한다.

---

## 10. 담당자별 역할

<table style="font-size: 0.8em; width: 100%; border-collapse: collapse; margin: 0; padding: 0;">
<tr>
  <th style="width: 15%; padding: 2px; text-align: left;">담당</th>
  <th style="width: 25%; padding: 2px; text-align: left;">역할</th>
  <th style="width: 60%; padding: 2px; text-align: left;">주요 내용</th>
</tr>
<tr>
  <td rowspan="4" style="padding: 2px;"><b>신대원</b></td>
  <td style="padding: 2px;">AI 툴 관리</td>
  <td style="padding: 2px;">Jira, Confluence, Slack, Claude 도입 및 AI 도구 관리</td>
</tr>
<tr>
  <td style="padding: 2px;">에이전트·룰·스킬 관리</td>
  <td style="padding: 2px;">AI 설정, 프롬프트 규칙, 에이전트 룰, 스킬 관리</td>
</tr>
<tr>
  <td style="padding: 2px;">전자정부프레임워크 테스트</td>
  <td style="padding: 2px;">전자정부 표준프레임워크 기반 코딩 자동화 테스트 수행</td>
</tr>
<tr>
  <td style="padding: 2px;">추진 총괄</td>
  <td style="padding: 2px;">AI 기반 프로젝트 관리 최적화 방향 수립 및 성과 관리</td>
</tr>
<tr>
  <td rowspan="4" style="padding: 2px;"><b>윤지혜</b></td>
  <td style="padding: 2px;">문서관리 전략 수립</td>
  <td style="padding: 2px;">정부기관 문서 템플릿 등록 및 산출물 관리 체계 수립</td>
</tr>
<tr>
  <td style="padding: 2px;">Jira/Confluence/Slack 문서관리</td>
  <td style="padding: 2px;">문서 작성·검토·취합 전략 수립</td>
</tr>
<tr>
  <td style="padding: 2px;">공정관리 자동화</td>
  <td style="padding: 2px;">Jira Task 취합 및 주간·월간 보고서 자동 생성</td>
</tr>
<tr>
  <td style="padding: 2px;">산출물 품질관리</td>
  <td style="padding: 2px;">산출물 누락, 검토·승인 상태 관리</td>
</tr>
<tr>
  <td rowspan="4" style="padding: 2px;"><b>강호일</b></td>
  <td style="padding: 2px;">에이전트 최적화</td>
  <td style="padding: 2px;">KOMSA 개발환경 맞춤 공통기능, 솔루션, API 지원</td>
</tr>
<tr>
  <td style="padding: 2px;">개발환경 표준화</td>
  <td style="padding: 2px;">개발환경, 공통 모듈, API 명세 정리</td>
</tr>
<tr>
  <td style="padding: 2px;">업무 테스트</td>
  <td style="padding: 2px;">해수호봇, RCMS 업무 AI 에이전트 성능 검증</td>
</tr>
<tr>
  <td style="padding: 2px;">기술 검증</td>
  <td style="padding: 2px;">생성 코드 품질, 테스트 통과율, 생산성 검증</td>
</tr>
<tr>
  <td rowspan="4" style="padding: 2px;"><b>박상원</b></td>
  <td style="padding: 2px;">컴포넌트 최적화</td>
  <td style="padding: 2px;">KOMSA 화면 패턴 분석 및 컴포넌트 명세 설정</td>
</tr>
<tr>
  <td style="padding: 2px;">화면 패턴 표준화</td>
  <td style="padding: 2px;">반복 화면, 공통 UI, 입력/조회/상세/승인 패턴 정리</td>
</tr>
<tr>
  <td style="padding: 2px;">업무 테스트</td>
  <td style="padding: 2px;">운항관리, 항만보안심사 업무 AI 에이전트 성능 검증</td>
</tr>
<tr>
  <td style="padding: 2px;">산출물 연계</td>
  <td style="padding: 2px;">화면정의서, 컴포넌트정의서, 테스트케이스 연결 검증</td>
</tr>
</table>

---

## 11. 단계별 추진 계획

#### [표 11-1] 단계별 추진 계획 및 일정(예시)

| 단계 | 항목            | 내용                                          | 기간(예시) |
| -- | ------------- | ------------------------------------------- | ------- |
| 1단계 | 도구 구성         | Jira, Confluence, Slack, Claude 기본 환경 구성    | 1개월 |
|     | 문서 템플릿        | 정부기관 산출물 템플릿 등록                             | 1개월 |
| 2단계 | Jira 구조       | 프로젝트, Issue Type, Workflow, Custom Field 설계 | 0.5개월 |
|      | Confluence 구조 | 산출물 Page Tree 및 AI Context 영역 구성            | 0.5개월 |
|      | Slack 채널      | 문서 요청, 검토, 보고, 개발, 이슈 채널 구성                 | 0.5개월 |
| 3단계 | 시범적용·검증       | 4개 업무 대상 시범적용 및 성과 측정                       | 3개월 |

마일스톤: M1 환경 구성 완료 → M2 표준 체계 확정 → M3 시범적용 성과 보고.

---

## 12. 기대효과(KPI)
**AI-Agent**를 활용하여 프로젝트 반복 수행하여 완성도 올라갈수록 비용 절감   

#### [표 12-1] 투입인력대체(예시) - 대규모 SI 프로젝트일 수록 효율적
| 항목 | 대체 내용 | 비용(예시) |
| --- | --- | --- |
| 사업관리, PMO, QA | PM - agent | IT품질관리자(9,692,094원) X M |
| AA | AA - agent | IT아키텍트(10,147,745원) X M |
| DA | DA - agent | 정보시스템운용자(10,154,626원) X M |
| UI/UX design | design - agent | UI/UX디자이너(5,176,203) X M |

#### [표 12-2] 핵심 성과지표(KPI, 예시)
| KPI | 개선 전(예시) | 목표(예시) |
| --- | --- | --- |
| 주간보고 작성시간 | 4시간/건 | 1.2시간/건 (70%↓) |
| 요구사항 추적 누락률 | 15% | 3% |
| 오픈 후 결함 건수 | 기준선 100% | 70% (30%↓) |
| 산출물 검토 리드타임 | 2~3일 | 1일 이내 |

---

## 13. 임원 의사결정 요청사항

본 과제 추진을 위해 다음 사항에 대한 의사결정이 필요하다.

#### [표 13-1] 의사결정 요청 항목

| 요청사항 | 내용 | 승인 시 효과 | 미승인 시 리스크 |
| --- | --- | --- | --- | 
| 도구 사용 승인 | Jira, Confluence, Figma, Claude 및 필요 AI 도구 사용 승인 | 자동화 체계 착수 가능 | 현행 수작업 비효율 지속 | 
| 시범 적용 승인 | 해수호봇, RCMS, 운항관리, 항만보안심사 대상 시범 적용 | 성과 검증 후 확대 근거 확보 | 효과 입증 지연 | 
| 디자인 지침 적용 | 범정부 UI/UX 가이드 기반 컴포넌트 정의서 적용 승인 | 화면 표준화·재사용성 확보 | 화면 산출물 품질 편차 | 

※ 시범적용 4개 업무는 규모·난이도·대표성을 고려해 선정하며, 선정 기준은 별첨으로 제시한다.

---

## 14. 결론

AI 기반 프로젝트 관리 최적화는 단순히 개발자가 AI로 코드를 생성하는 수준의 도입이 아니다. 공공기관 프로젝트의 핵심 리스크인 **문서 품질, 요구사항 추적성, 공정률 정확성, 개발 품질, 감리 대응력**을 개선하기 위한 프로젝트 수행 방식의 전환이다.

Jira, Confluence, Slack, Claude를 중심으로 프로젝트 역할과 워크플로우를 표준화하고, AI CLI 도구를 활용하여 요구사항 분석, 계획 수립, TDD, 작업 분해, 보고서 생성까지 자동화하면 다음 효과를 기대할 수 있다.

#### [표 14-1] 기대효과 요약

| 기대효과 | 내용 |
| --- | --- |
| 문서 품질 향상 | 표준 템플릿·자동 검토로 산출물 일관성 확보 |
| 요구사항 추적성 강화 | ID 체인 자동 점검으로 감리 대응력 향상 |
| 공정관리 정확도 향상 | 테스트 통과 기반 객관적 공정률 |
| 보고 업무 시간 단축 | 주간·월간보고 자동 생성 |
| 개발 품질 향상 | SDD+TDD 기반 선제적 품질 확보 |
| 감리·검수 대응력 강화 | 추적표·산출물 현황 자동화 |
| AI 기반 업무혁신 체계 정착 | 역할·룰·스킬 표준화 |

---
# 시연 egov-da

> **egov-da** — 공공데이터베이스 표준화(전자정부 / eGovFramework)를 위한 DA(Data
> Architecture) 자동화 플러그인. 
> 요구사항 → 데이터 모델링 → 메타데이터 → 표준화 → 구조 검증 → (선택)문서·DB 구축의 파이프라인을 오케스트레이션한다.

---

## 에이전트 팀 (5)

| 에이전트 | 모델 | 역할 | 배경 스킬 | harness 패턴 | 호출 시점 |
|---|---|---|---|---|---|
| **slack-agent** | opus | Slack 진입점 — 명령 파싱 → 대상 에이전트 워크플로우 조회 → TodoList 구성 → Slack 진행 스트리밍 | `slack-orchestrator` | Supervisor / Dispatcher | Slack 멘션 수신 시 |
| **da-agent** | opus | DA 파이프라인 — 모델링 → **(필수) 표준화 검토** → 최종 ERD/테이블/컬럼 정의 | `da-orchestrator` (+ data-modeling, …) | Producer→Reviewer + Pipeline | 데이터 모델링·DB 설계·산출물 요청 시 |
| **metadata-agent** | sonnet | 표준화 권위 — 공공(읽기전용) → 기관({domain}); 용어→단어→도메인→코드 순 검토, 없으면 생성 | `metadata-standardize` | Reviewer / Authority | da-agent 2단계(필수 게이트) |
| **dba-agent** | opus | DB 구축 — Docker Oracle/PostgreSQL 프로비저닝, DDL 파일+실행, CRUD SQL | `dba-orchestrator` (+ db-provisioning, …) | Pipeline (downstream) | DA 산출물 확정 후 구축 요청 시 |
| **document-agent** | sonnet | (선택) 산출물 문서(md/xlsx) 작성 + Confluence 발행 | `data-output-management`, `confluence-integration` | Delegated worker | 요청 시에만 (게이트 아님) |

---

## 오케스트레이션 흐름

```
Slack ─▶ slack-agent ─(라우팅)─▶ da-agent ──(필수)──▶ metadata-agent
                                    │  ▲ 환류 (확인 필요)
                                    │  └────────────────────┘
                                    ├─(선택)─▶ document-agent ─▶ Confluence
                                    └─(후속)─▶ dba-agent ─▶ 실 DB + CRUD
```

- **slack-agent**는 단계를 하드코딩하지 않는다. 대상 에이전트의 오케스트레이터
  워크플로우(da 7단계 / dba 3단계)를 읽어 **그대로** TodoList에 등록하고, 각
  TodoWrite 갱신마다 Slack 알림을 발송한다.
- **da-agent → metadata-agent**는 **필수 게이트**다. `미검토` 상태로 남은 표준화
  산출물은 게이트를 실패시키고 1단계로 환류한다. `확인 필요`(후보 ≥2)는 동일
  에이전트에 `SendMessage`로 재질의해 컨텍스트를 유지한다.
- **da-agent → document-agent**는 **선택**이며, 요청 시에만 동작한다 (파이프라인을
  막지 않는다).
- **da-agent → dba-agent**는 **후속 구축**으로, 실제 DDL/CRUD를
  `docs/05. db-build/{reqid}/`에 영속화한다.

---

## DA 파이프라인 (da-agent, 7단계 + 상시)

`da-orchestrator` 스킬이 정의한다. 각 단계는 산출물 파일을 남기며 다음 단계의 입력이 된다.

| # | 단계 | 호출 | 소유(스킬/에이전트) | 산출물 |
|---|------|------|---------------------|--------|
| 1 | 데이터 모델링 | Skill | `data-modeling` | `{reqid}-db-modeling.md` |
| 2 | 표준화 검토 | Agent | `metadata-agent` / `metadata-standardize` | `{reqid}-표준검토결과.xlsx`, `{reqid}-column-spec.md` |
| 3 | 데이터 구조 검증 | Skill | `data-structure-verification` | `{reqid}-구조검증결과.md` (적합/보완/부적합) |
| 4 | 산출물 관리 | Skill | `data-output-management` | 산출물 7종 + 산출물관리대장 xlsx |
| 5 | 변경 관리 | Skill | `db-decision-records` + `db-migrations` | `adr/*.md`, `migrations/*.sql` |
| 6 | 품질 관리 | Skill | `data-quality-management` | `{reqid}-데이터품질부적합대장.xlsx` |
| 7 | 데이터 분석 | Skill | `data-analysis` | `{reqid}-데이터분석노트.md` |
| 9 | 산출물 등록(**선택**) | Skill | `confluence-integration` + document-agent | Confluence 페이지+첨부(링크) |

**산출물 7종(4단계):** 논리 ERD · 물리 ERD · 엔터티 정의서 · 애트리뷰트 정의서 ·
DB 정의서 · 테이블 정의서 · 컬럼 정의서 (+ 산출물관리대장). 각 `{reqid}-{name}.xlsx`는
본문 시트 + 변경이력 시트로 구성되며 컬럼 규격은
`data-output-management/references/column-specs.md`를 따른다.

---

## DBA 구축 파이프라인 (dba-agent, 3단계)

DA 산출물이 준비되면 실 DB 구축으로 확장한다. `dba-orchestrator`가 정의하며 DA
파이프라인과 분리해 추가 TodoList로 추적한다.

| 단계 | 스킬 | 내용 / 게이트 |
|---|---|---|
| 1. 프로비저닝 | `db-provisioning` | Docker Oracle/PostgreSQL 기동 → healthcheck |
| 2. 객체 생성 | `db-object-creation` | DDL 파일 작성 + 실행 → 정의서 대조 검증 |
| 3. CRUD 생성 | `crud-sql-generation` | 바인드 변수 기반 CRUD SQL (`sql/{table}_crud.sql`) |

- 대상 DBMS(Oracle/PostgreSQL)로 분기하며, 표준 용어 약어·도메인 타입/길이는 임의 변경
  금지. 정의↔객체 불일치는 da-agent로 환류한다.
- DDL은 `docs/05. db-build/{reqid}/ddl/*.sql`에 반드시 파일로 남긴다(파일 없는 DB 생성 금지).
- 비밀번호는 env 주입, 바인드 변수만 사용(문자열 연결 `${}` 금지), prod 무단 실행·볼륨
  삭제 금지.

---

## 코드 & 자산 위치

| 관심사 | 위치 |
|---|---|
| 에이전트 정의 | `.claude/agents/{slack,da,metadata,dba,document}-agent.md` |
| 스킬(절차) | `.claude/skills/<name>/SKILL.md` |
| Slack 런타임 | `python/agent/slack-agent/` (bot receiver, review agent) |
| 진행 알림 | `python/project/notify/da_progress_notify.py` |
| 메타데이터 툴링 | `python/agent/metadata-agent/` (index/sync) |
| 문서/Confluence | `python/agent/document-agent/` |
| 표준 룰(지연 로드) | `.claude/docs/standards/` |
| 메타데이터 사전 | `docs/03. metadata/{공공,기관}/*.tsv` |
| 시크릿 | `.claude/.env` (gitignore) |

---
## 부록. ECC 상세 구성

본문 7.1·7.2의 ECC 자원관리/워크플로우 상세 다이어그램과 8.3 디렉터리 구조는 기술 청중을 위한 참고자료로 본 부록에 함께 둔다. 임원 보고 시에는 6~8장의 구성도 중심으로 설명하고, 상세 동작은 본 부록을 참조한다.

### 7.1 ECC 자원관리
```mermaid
flowchart LR
    TASK[작업 요청] --> CTX[Context Window]
    CTX --> SKILL[필요 Skill만 로드]
    CTX --> MCP[MCP 최소 활성화]
    CTX --> AGENT[역할별 Agent 분리]

    AGENT --> TOKEN[Token Cost]
    SKILL --> TOKEN
    MCP --> TOKEN

    TOKEN --> COMPACT[Strategic Compact]
    COMPACT --> MEM[Memory Persistence]
    MEM --> NEXT[다음 세션 재사용]

    HOOK[Hooks] --> GUARD[보안/품질 자동 검사]
    HOOK --> SAVE[세션 저장]
    HOOK --> WARN[Compact 제안]
```
[그림 7-2] ECC 자원관리 구조

---

### 7.2 클로드 Workflow

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Harness as Claude Code/Codex/Gemini
    participant Command as Command
    participant Agent as Agent
    participant Skill as Skill
    participant Rule as Rule
    participant Hook as Hook
    participant MCP as MCP Server
    participant Memory as Memory
    participant Output as Output

    User->>Harness: 작업 요청 또는 slash command
    Harness->>Command: 명령 해석
    Command->>Agent: 적합한 Agent 위임
    Agent->>Skill: 관련 Skill 로드
    Agent->>Rule: 공통/언어/보안 규칙 적용
    Hook->>Agent: 실행 전 검사
    Agent->>MCP: 필요 시 외부 도구 호출
    MCP-->>Agent: 외부 데이터/도구 결과 반환
    Agent->>Output: 코드/문서/테스트 생성
    Hook->>Output: 실행 후 검사/포맷/경고
    Agent->>Memory: 세션 요약/학습 패턴 저장
    Output-->>User: 최종 결과 반환
```
[그림 7-3] ECC 워크플로우

### 8.3 프로젝트 구성도

```text
egov-ecc/
├─ agents/orchestrator
│  ├─ pm-agent.md
│  ├─ biz-management-agent.md
│  ├─ egov-architecture.md
│  ├─ egov-db-agent.md
│  ├─ egov-design-agent.md
│  ├─ egov-developer-agent.md
│  ├─ reviewer.md
│  ├─ deployer.md
│  └─ qa-agent.md
│
├─ skills/
│  ├─ egov-document-template/
│  ├─ egov-requirement-analysis/
│  ├─ egov-framework-patterns/
│  ├─ egov-menu-auth-check/
│  ├─ egov-server-security/
│  ├─ egov-test-scenarios/
│  ├─ realtime-meeting-minutes/
│  ├─ SDD/
│  ├─ ECC/
│  └─ ETC..
│
├─ commands/
│  ├─ egov-plan.md
│  ├─ egov-generate-code.md
│  ├─ egov-security-check.md
│  ├─ egov-menu-auth-check.md
│  ├─ egov-meeting-close.md
│  └─ egov-acceptance-doc.md
│
├─ rules/ (egov-wiki 기반 작성 지침 생성)
│  ├─ common-base-rule.md
│  ├─ screen-processing-rule.md
│  ├─ business-processing-rule.md
│  ├─ data-processing-rule.md
│  ├─ integration-rule.md
│  ├─ batch-rule.md
│  └─ security-rule.md
│
├─ hooks/
│  ├─ before-submit-secret-check.json
│  ├─ after-file-edit-format.json
│  ├─ suggest-compact.json
│  └─ session-memory.json
│
├─ mcp-configs/
│  ├─ github.json
│  ├─ jira.json
│  ├─ confluence.json
│  ├─ figma.json
│  ├─ slack.json
│  ├─ db-readonly.json
│  └─ playwright.json
│
├─ docs/
│  ├─ reference/
│  └─ workspace/
│
├─ run/
│
└─ outputs/
   ├─ jira/
   ├─ confluence/
   ├─ meeting-minutes/
   ├─ test-results/
   └─ acceptance-docs/
```

```text
src/main/webapp/WEB-INF/jsp/egovframework/let/<domain>/<module>/
├── Egov<Module>List.jsp
├── Egov<Module>Regist.jsp
├── Egov<Module>Detail.jsp
└── Egov<Module>Updt.jsp

src/main/java/egovframework/let/<domain>/<module>/
├── web/
│   └── Egov<Module>Controller.java
├── service/
│   ├── Egov<Module>Service.java
│   ├── <Module>VO.java
│   └── <Module>.java
└── service/impl/
    ├── Egov<Module>ServiceImpl.java
    └── <Module>DAO.java

src/test/java/egovframework/let/<domain>/<module>/
├── web/Egov<Module>ControllerTest.java
├── service/Egov<Module>ServiceTest.java
└── service/impl/<Module>DAOTest.java
```
[그림 8-3] 프로젝트 디렉터리 및 산출물 구조

---
