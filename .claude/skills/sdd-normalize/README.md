# SDD Normalize Skill

수집된 문서를 Markdown으로 정규화합니다.

## 사용법

```
/sdd-normalize
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| workspace | 저장 위치 | ✅ | /tmp/sdd-workspaces |
| requirement_id | 요구사항 ID | ✅ | REQ-001 |

## 예시

```
저장 위치: /tmp/sdd-workspaces
요구사항 ID: REQ-001
```

## 동작

1. `/tmp/sdd-workspaces/REQ-001/input` 디렉터리 확인
2. DOCX/XLSX/PPTX/HWPX/PDF 파일 자동 감지
3. 각 파일을 Markdown으로 변환
4. `/tmp/sdd-workspaces/REQ-001/normalized` 디렉터리에 저장

## 지원 포맷

| 입력 | 출력 | 라이브러리 |
|-----|------|----------|
| DOCX | Markdown + 테이블 | python-docx |
| XLSX | Markdown Table | openpyxl |
| PPTX | Markdown (슬라이드별) | python-pptx |
| HWPX | Markdown (부분) | zipfile |
| PDF | Markdown (텍스트) | PyPDF2 |
| HTML | Markdown | html2text |
| Markdown | 그대로 | - |

## 출력

```
✅ 문서 정규화 완료
총 파일: 6개
성공: 6개
저장 위치: /tmp/sdd-workspaces/REQ-001/normalized
```

## 생성 구조

```
/tmp/sdd-workspaces/REQ-001/
├── input/
│   ├── 요구사항정의서_v0.3.docx
│   └── 테스트케이스_v0.1.xlsx
│
└── normalized/        ⭐ 정규화 완료
    ├── 요구사항정의서_v0.3.md
    └── 테스트케이스_v0.1.md
```

## 관련 문서

- [SDD Workflow Guide](../../../scripts/SDD_WORKFLOW.md)
