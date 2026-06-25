"""Speckit 워크플로우 자동 실행"""

import subprocess
import logging
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SpeckitRunner:
    """Speckit 워크플로우 자동 실행기"""

    def __init__(self, workspace_dir: Path):
        """
        초기화

        Args:
            workspace_dir: Speckit Workspace 디렉터리
        """
        self.workspace_dir = Path(workspace_dir)
        self.input_dir = self.workspace_dir / "input"
        self.normalized_dir = self.workspace_dir / "normalized"
        self.specs_dir = self.workspace_dir / "specs"
        self.specs_dir.mkdir(parents=True, exist_ok=True)

        self.execution_log = []

    def initialize_workspace(self) -> bool:
        """
        Speckit Workspace 초기화

        Returns:
            성공 여부
        """
        logger.info(f"🔧 Speckit Workspace 초기화 중...")

        try:
            # 1. .specify 디렉터리 생성
            specify_dir = self.workspace_dir / ".specify"
            specify_dir.mkdir(parents=True, exist_ok=True)

            # 2. 기본 구성 파일 생성
            self._create_specify_config()

            # 3. specs 디렉터리 생성
            self.specs_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"✓ Workspace 초기화 완료: {self.workspace_dir}")
            self.execution_log.append({
                "step": "initialize",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
            })
            return True

        except Exception as e:
            logger.error(f"✗ Workspace 초기화 실패: {e}")
            self.execution_log.append({
                "step": "initialize",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return False

    def run_specify(self) -> Dict[str, Any]:
        """
        /speckit.specify 명령 실행

        Returns:
            실행 결과 및 생성 파일
        """
        logger.info(f"📋 /speckit.specify 실행 중...")

        stats = {
            "success": False,
            "command": "specify",
            "generated_files": [],
            "error": None,
        }

        try:
            # 1. 입력 문서 준비
            input_files = self._prepare_input_files()
            if not input_files:
                logger.warning("입력 파일이 없습니다")
                stats["error"] = "No input files"
                return stats

            logger.info(f"   입력 파일: {len(input_files)}개")

            # 2. Speckit 명령 구성
            prompt = self._build_specify_prompt(input_files)

            # 3. Claude API 호출 (실제로는 specify 스킬 사용)
            # 현재는 모의 구현 - 실제로는 Claude API 또는 specify CLI 호출
            result = self._call_speckit_api(prompt, "specify")

            if not result:
                stats["error"] = "Speckit API call failed"
                return stats

            # 4. 생성 파일 수집
            generated_files = self._collect_specify_artifacts(result)
            stats["generated_files"] = generated_files
            stats["success"] = True

            logger.info(f"✓ /speckit.specify 완료: {len(generated_files)}개 파일 생성")
            self.execution_log.append({
                "step": "specify",
                "status": "success",
                "files_generated": len(generated_files),
                "timestamp": datetime.now().isoformat(),
            })

            return stats

        except Exception as e:
            logger.error(f"✗ /speckit.specify 실패: {e}")
            stats["error"] = str(e)
            self.execution_log.append({
                "step": "specify",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return stats

    def run_plan(self) -> Dict[str, Any]:
        """
        /speckit.plan 명령 실행

        Returns:
            실행 결과 및 생성 파일
        """
        logger.info(f"📐 /speckit.plan 실행 중...")

        stats = {
            "success": False,
            "command": "plan",
            "generated_files": [],
            "error": None,
        }

        try:
            # 1. 입력 파일 확인 (requirements.md, spec.md)
            input_files = self._prepare_plan_input_files()
            if not input_files:
                logger.warning("Plan 입력 파일이 없습니다")
                stats["error"] = "No input files for plan"
                return stats

            # 2. Speckit 명령 구성
            prompt = self._build_plan_prompt(input_files)

            # 3. Claude API 호출
            result = self._call_speckit_api(prompt, "plan")

            if not result:
                stats["error"] = "Speckit API call failed"
                return stats

            # 4. 생성 파일 수집
            generated_files = self._collect_plan_artifacts(result)
            stats["generated_files"] = generated_files
            stats["success"] = True

            logger.info(f"✓ /speckit.plan 완료: {len(generated_files)}개 파일 생성")
            self.execution_log.append({
                "step": "plan",
                "status": "success",
                "files_generated": len(generated_files),
                "timestamp": datetime.now().isoformat(),
            })

            return stats

        except Exception as e:
            logger.error(f"✗ /speckit.plan 실패: {e}")
            stats["error"] = str(e)
            self.execution_log.append({
                "step": "plan",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return stats

    def run_tasks(self) -> Dict[str, Any]:
        """
        /speckit.tasks 명령 실행

        Returns:
            실행 결과 및 생성 파일
        """
        logger.info(f"✅ /speckit.tasks 실행 중...")

        stats = {
            "success": False,
            "command": "tasks",
            "generated_files": [],
            "error": None,
        }

        try:
            # 1. 입력 파일 확인
            input_files = self._prepare_tasks_input_files()
            if not input_files:
                logger.warning("Tasks 입력 파일이 없습니다")
                stats["error"] = "No input files for tasks"
                return stats

            # 2. Speckit 명령 구성
            prompt = self._build_tasks_prompt(input_files)

            # 3. Claude API 호출
            result = self._call_speckit_api(prompt, "tasks")

            if not result:
                stats["error"] = "Speckit API call failed"
                return stats

            # 4. 생성 파일 수집
            generated_files = self._collect_tasks_artifacts(result)
            stats["generated_files"] = generated_files
            stats["success"] = True

            logger.info(f"✓ /speckit.tasks 완료: {len(generated_files)}개 파일 생성")
            self.execution_log.append({
                "step": "tasks",
                "status": "success",
                "files_generated": len(generated_files),
                "timestamp": datetime.now().isoformat(),
            })

            return stats

        except Exception as e:
            logger.error(f"✗ /speckit.tasks 실패: {e}")
            stats["error"] = str(e)
            self.execution_log.append({
                "step": "tasks",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return stats

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """실행 로그 반환"""
        return self.execution_log

    def save_execution_log(self) -> Path:
        """실행 로그 저장"""
        log_file = self.workspace_dir / "speckit-execution.json"

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 실행 로그 저장: {log_file}")
        return log_file

    # ===== 내부 메서드 =====

    def _create_specify_config(self):
        """기본 설정 파일 생성"""
        config = {
            "project": "egov-demo",
            "description": "전자정부표준프레임워크 SDD 자동화",
            "created_at": datetime.now().isoformat(),
        }

        config_file = self.workspace_dir / ".specify" / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _prepare_input_files(self) -> List[Path]:
        """Specify 입력 파일 준비"""
        input_files = []

        # normalized 디렉터리의 Markdown 파일
        if self.normalized_dir.exists():
            for md_file in self.normalized_dir.rglob("*.md"):
                input_files.append(md_file)

        # 폴백: input 디렉터리
        if not input_files and self.input_dir.exists():
            for md_file in self.input_dir.rglob("*.md"):
                input_files.append(md_file)

        return sorted(input_files)

    def _prepare_plan_input_files(self) -> List[Path]:
        """Plan 입력 파일 준비"""
        plan_files = []

        # specs 디렉터리의 requirements.md, spec.md
        specs_dir = self.specs_dir
        for name in ["requirements.md", "spec.md"]:
            file_path = specs_dir / name
            if file_path.exists():
                plan_files.append(file_path)

        return plan_files

    def _prepare_tasks_input_files(self) -> List[Path]:
        """Tasks 입력 파일 준비"""
        tasks_files = []

        # specs 디렉터리의 필수 파일
        specs_dir = self.specs_dir
        for name in ["spec.md", "plan.md", "component_spec.md"]:
            file_path = specs_dir / name
            if file_path.exists():
                tasks_files.append(file_path)

        return tasks_files

    def _build_specify_prompt(self, input_files: List[Path]) -> str:
        """Specify 프롬프트 구성"""
        prompt = """
# Speckit Specify 명령

다음 입력 문서를 기반으로 요구사항을 체계화합니다.

## 입력 문서
"""
        for file_path in input_files:
            prompt += f"\n- {file_path.name}"

        prompt += """

## 생성 목표
1. requirements.md - 요구사항 정의
2. spec.md - 명세서
3. edge_cases.md - 모호한 항목 및 질문

## 기술 기준
- Java 17, Spring Boot
- 전자정부프레임워크 5.0
- MyBatis, Oracle 11g
- JUnit 5 테스트

## 출력 형식
각 파일을 별도로 생성하고 다음 구조를 유지합니다:
- requirements.md: REQ-FN-001, REQ-NF-001 등 ID 포함
- spec.md: 유스케이스와 테스트케이스 연결
- edge_cases.md: 확인 필요 항목 리스트
"""
        return prompt

    def _build_plan_prompt(self, input_files: List[Path]) -> str:
        """Plan 프롬프트 구성"""
        prompt = """
# Speckit Plan 명령

다음 요구사항을 기반으로 구현 계획을 수립합니다.

## 입력 파일
"""
        for file_path in input_files:
            prompt += f"\n- {file_path.name}"

        prompt += """

## 생성 목표
1. plan.md - 구현 계획
2. component_spec.md - 컴포넌트 설명
3. data_model.md - 데이터 모델

## 기술 기준
- Java 17, Spring Boot
- Controller-Service-DAO 구조
- MyBatis SQL Mapper
- Oracle 11g ROWNUM 페이징
- JUnit 5 + MockMvc 테스트

## 추적성
- 요구사항 ID 유지
- 테스트케이스 ID 연결
- 변경사항 기록
"""
        return prompt

    def _build_tasks_prompt(self, input_files: List[Path]) -> str:
        """Tasks 프롬프트 구성"""
        prompt = """
# Speckit Tasks 명령

설계 문서를 기반으로 구현 작업을 분해합니다.

## 입력 파일
"""
        for file_path in input_files:
            prompt += f"\n- {file_path.name}"

        prompt += """

## 생성 목표
tasks.md - 실행 가능한 작업 목록

## 작업 구성
- Story별 구성
- 각 Story의 Sub-task (T001, T002, ...)
- 테스트 우선순위
- 요구사항 ID 연결

## 우선순위
1. 테스트 코드 작성 (TDD)
2. DTO 및 엔티티 정의
3. Service 구현
4. Mapper SQL 작성
5. Controller 구현
6. 통합 테스트
"""
        return prompt

    def _call_speckit_api(self, prompt: str, command: str) -> Optional[Dict[str, Any]]:
        """
        Speckit API 호출 (모의 구현)

        실제로는 Claude API 또는 specify CLI를 호출합니다.
        """
        # 모의 구현: 프롬프트를 파일로 저장하고 반환
        logger.debug(f"   Speckit {command} API 호출...")

        result = {
            "command": command,
            "status": "success",
            "artifacts": self._generate_mock_artifacts(command),
        }

        return result

    def _generate_mock_artifacts(self, command: str) -> Dict[str, str]:
        """모의 산출물 생성"""
        artifacts = {}

        if command == "specify":
            artifacts["requirements.md"] = """# 요구사항정의서

## 기능 요구사항

### REQ-FN-001: 사용자 조회
- 사용자 목록을 페이징으로 조회한다
- 사용자명 검색 지원

### REQ-FN-002: 사용자 등록
- 신규 사용자를 등록한다
"""
            artifacts["spec.md"] = """# 명세서

## 시스템 아키텍처

Controller → Service → DAO → Mapper SQL

## API 설계

- GET /users - 사용자 목록 조회
- GET /users/{id} - 사용자 상세
- POST /users - 사용자 등록
"""
            artifacts["edge_cases.md"] = """# 모호한 항목 및 질문

## 질문 1: 중복 사용자 처리
- 동일 사용자명의 중복 등록 정책?
- 차단 vs 경고 vs 허용?

## 질문 2: 페이징 크기
- 기본 페이지 크기는 몇 개?
- 최대 페이지 크기는?
"""

        elif command == "plan":
            artifacts["plan.md"] = """# 구현 계획

## Phase 1: 기초 구현 (1주)
- VO/DTO 정의
- Service 인터페이스
- Mapper SQL

## Phase 2: 테스트 (3일)
- JUnit 테스트 작성
- 통합 테스트

## Phase 3: 마무리 (2일)
- 리뷰 및 최적화
"""
            artifacts["component_spec.md"] = """# 컴포넌트 설명

## UserController
- /users GET: 목록 조회
- /users POST: 등록

## UserService
- selectList()
- selectDetail()
- insertUser()

## UserDAO
- 매퍼 호출
"""
            artifacts["data_model.md"] = """# 데이터 모델

## USER_TBL
- USER_ID (PK)
- USER_NAME
- REG_USR_ID
- FRST_REGIST_PNTTM
"""

        elif command == "tasks":
            artifacts["tasks.md"] = """# 작업 분해

## Story 1: 사용자 조회 기능

- [ ] T001 UserVO/UserDefaultVO 정의
- [ ] T002 UserService 인터페이스
- [ ] T003 UserController 테스트
- [ ] T004 UserController 구현
- [ ] T005 UserServiceImpl 구현
- [ ] T006 UserDAO 정의
- [ ] T007 UserMapper.xml SQL
- [ ] T008 JUnit 통합 테스트
"""

        return artifacts

    def _collect_specify_artifacts(self, result: Dict[str, Any]) -> List[str]:
        """Specify 산출물 수집"""
        artifacts = []
        artifacts_dict = result.get("artifacts", {})

        for name, content in artifacts_dict.items():
            file_path = self.specs_dir / name
            file_path.write_text(content, encoding='utf-8')
            artifacts.append(str(file_path))
            logger.debug(f"   💾 {name} 저장됨")

        return artifacts

    def _collect_plan_artifacts(self, result: Dict[str, Any]) -> List[str]:
        """Plan 산출물 수집"""
        artifacts = []
        artifacts_dict = result.get("artifacts", {})

        for name, content in artifacts_dict.items():
            file_path = self.specs_dir / name
            file_path.write_text(content, encoding='utf-8')
            artifacts.append(str(file_path))
            logger.debug(f"   💾 {name} 저장됨")

        return artifacts

    def _collect_tasks_artifacts(self, result: Dict[str, Any]) -> List[str]:
        """Tasks 산출물 수집"""
        artifacts = []
        artifacts_dict = result.get("artifacts", {})

        for name, content in artifacts_dict.items():
            file_path = self.specs_dir / name
            file_path.write_text(content, encoding='utf-8')
            artifacts.append(str(file_path))
            logger.debug(f"   💾 {name} 저장됨")

        return artifacts
