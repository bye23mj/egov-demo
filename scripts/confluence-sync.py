#!/usr/bin/env python3
"""
Confluence 문서 동기화 + JIRA 연동 CLI

사용법:
    python scripts/confluence-sync.py download        # Confluence → 로컬
    python scripts/confluence-sync.py upload          # 로컬 → Confluence
    python scripts/confluence-sync.py sync            # 양방향 동기화
    python scripts/confluence-sync.py status          # 동기화 상태 조회
    python scripts/confluence-sync.py config          # 설정 조회/변경

    python scripts/confluence-sync.py jira config     # JIRA 설정 관리
    python scripts/confluence-sync.py jira status     # JIRA 연결 확인
    python scripts/confluence-sync.py jira search     # JIRA 이슈 검색
"""

import sys
import logging
import argparse
from pathlib import Path

# 스크립트 경로를 Python 패스에 추가
sys.path.insert(0, str(Path(__file__).parent))

from confluence.config import config
from confluence.sync import ConfluenceSync
from confluence.jira_api import JiraAPI, JiraConfig
from confluence.document_collector import DocumentCollector
from confluence.document_normalizer import DocumentNormalizer
from confluence.speckit_runner import SpeckitRunner


def setup_logging(verbose: bool = False):
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                Path(config.get("local_folder")).parent / ".confluence-sync.log",
                encoding="utf-8"
            )
        ]
    )


def print_stats(stats: dict, operation: str):
    """통계 출력"""
    print(f"\n{'─'*40}")
    print(f"  {operation} 완료")
    print(f"{'─'*40}")
    for key, value in stats.items():
        emoji = "✓" if key != "errors" or value == 0 else "✗"
        print(f"  {emoji} {key}: {value}")
    print(f"{'─'*40}\n")


def cmd_config(args):
    """설정 명령어 처리"""
    if args.set_token:
        # 토큰을 환경변수 파일에 저장
        env_file = Path.home() / ".confluence-sync" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_file, "w") as f:
            f.write(f"CONFLUENCE_TOKEN={args.set_token}\n")
        import os
        os.chmod(env_file, 0o600)
        print("✓ Token saved securely to ~/.confluence-sync/.env")
    elif args.show:
        cfg = config.display()
        print("\n현재 설정:")
        print("─" * 40)
        for key, value in cfg.items():
            print(f"  {key}: {value}")
        print("─" * 40)
    else:
        print("사용법: confluence-sync config --show | --set-token <token>")


def cmd_status(args):
    """상태 조회"""
    syncer = ConfluenceSync()
    status = syncer.status()
    print("\n📊 Confluence 동기화 상태")
    print("─" * 50)
    for key, value in status.items():
        print(f"  {key}: {value}")
    print("─" * 50)

    # 연결 테스트
    print("\n🔌 연결 테스트 중...")
    if syncer.api.test_connection():
        print("✓ Confluence 연결 성공")
    else:
        print("✗ Confluence 연결 실패 - 토큰 및 설정을 확인하세요")


def cmd_download(args):
    """다운로드 명령어"""
    print(f"⬇  Confluence → 로컬 다운로드 시작")
    print(f"   폴더: {config.get('local_folder')}")
    syncer = ConfluenceSync()
    stats = syncer.download(force=args.force)
    print_stats(stats, "다운로드")


def cmd_upload(args):
    """업로드 명령어"""
    if args.dry_run:
        print("🔍 [DRY-RUN] 실제 업로드 없이 대상만 확인합니다")
    else:
        print(f"⬆  로컬 → Confluence 업로드 시작")
    syncer = ConfluenceSync()
    stats = syncer.upload(dry_run=args.dry_run)
    print_stats(stats, "업로드 (DRY-RUN)" if args.dry_run else "업로드")


def cmd_sync(args):
    """양방향 동기화"""
    print(f"🔄 양방향 동기화 시작")
    if args.local_overwrite:
        print("   충돌 정책: 로컬 우선")
    elif args.confluence_overwrite:
        print("   충돌 정책: Confluence 우선")
    syncer = ConfluenceSync()
    stats = syncer.sync(
        local_overwrite=args.local_overwrite,
        confluence_overwrite=args.confluence_overwrite,
    )
    print_stats(stats, "동기화")


def cmd_jira_config(args):
    """JIRA 설정 관리"""
    jira_config = JiraConfig()

    if args.set_token:
        import os
        env_file = Path.home() / ".jira-sync" / ".env"
        env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(env_file, "w") as f:
            f.write(f"JIRA_TOKEN={args.set_token}\n")
        os.chmod(env_file, 0o600)
        print("✓ JIRA Token saved securely to ~/.jira-sync/.env")
    elif args.show:
        cfg = jira_config.display()
        print("\n현재 JIRA 설정:")
        print("─" * 50)
        for key, value in cfg.items():
            print(f"  {key}: {value}")
        print("─" * 50)
    else:
        print("사용법: jira config --show | --set-token <token>")


def cmd_jira_status(args):
    """JIRA 연결 상태 확인"""
    print("\n🔌 JIRA 연결 테스트 중...")
    try:
        api = JiraAPI()
        if api.test_connection():
            print("✓ JIRA 연결 성공")
            print(f"  Project Key: {api.project_key}")
            print(f"  URL: {api.base_url}")
        else:
            print("✗ JIRA 연결 실패")
    except Exception as e:
        print(f"✗ 오류 발생: {e}")


def cmd_jira_search(args):
    """JIRA 이슈 검색"""
    try:
        api = JiraAPI()

        print(f"\n🔍 JIRA 이슈 검색")
        print(f"   상태: {args.status}")
        print(f"   문서 유형: {', '.join(args.document_types)}")

        issues = api.get_issues_by_status(args.status, args.document_types)

        print(f"\n검색 결과: {len(issues)}건")
        print("─" * 60)

        for issue in issues:
            key = issue.get("key")
            fields = issue.get("fields", {})
            summary = fields.get("summary", "")
            status = fields.get("status", {}).get("name", "")

            attachments = fields.get("attachment", [])
            doc_count = len(attachments)

            print(f"  {key}: {summary}")
            print(f"    상태: {status}, 첨부파일: {doc_count}건")

        print("─" * 60)

    except Exception as e:
        logging.error(f"✗ 검색 실패: {e}")


def cmd_collect(args):
    """SDD 문서 수집"""
    from datetime import datetime
    import uuid

    # Run ID 생성 (RUN-20260611-001 형식)
    date_str = datetime.now().strftime("%Y%m%d")
    run_id = f"RUN-{date_str}-{uuid.uuid4().hex[:3].upper()}"

    # Workspace 디렉터리 생성
    workspace_dir = Path(args.workspace) / run_id
    workspace_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 SDD 문서 수집 시작")
    print(f"   Run ID: {run_id}")
    print(f"   Workspace: {workspace_dir}")
    print(f"   Status: {args.status}")
    print(f"   Document Types: {', '.join(args.document_types)}")

    try:
        collector = DocumentCollector(run_id, workspace_dir)

        # JIRA에서 문서 수집
        print(f"\n⬇  JIRA에서 문서 수집 중...")
        jira_stats = collector.collect_from_jira_status(
            status=args.status,
            document_types=args.document_types,
        )

        # 메타데이터 저장
        print(f"\n💾 메타데이터 저장 중...")
        metadata_file = collector.save_metadata(
            project_key=args.project_key,
            target_status=args.status,
            phase="collect",
            notes=f"자동 수집: {args.status} 상태의 문서",
        )

        # 통계 출력
        stats = collector.get_stats()

        print(f"\n✅ 문서 수집 완료")
        print(f"─" * 50)
        print(f"  Run ID: {run_id}")
        print(f"  수집된 문서: {stats['total_documents']}개")
        print(f"    - JIRA에서: {stats['from_jira']}개")
        print(f"    - Confluence에서: {stats['from_confluence']}개")
        print(f"  Workspace: {stats['workspace_path']}")
        print(f"  메타데이터: {metadata_file}")
        print(f"─" * 50)

        if jira_stats['errors'] > 0:
            print(f"\n⚠️  {jira_stats['errors']}개 문서 수집 실패")

    except Exception as e:
        logging.error(f"✗ 수집 실패: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_normalize(args):
    """SDD 문서 정규화 (→ Markdown)"""
    input_dir = Path(args.run_id) / "input"
    normalized_dir = Path(args.run_id) / "normalized"

    if not input_dir.exists():
        print(f"✗ input 디렉터리 없음: {input_dir}")
        sys.exit(1)

    print(f"\n🔄 문서 정규화 시작")
    print(f"   Run ID: {args.run_id}")
    print(f"   입력: {input_dir}")
    print(f"   출력: {normalized_dir}")

    try:
        normalizer = DocumentNormalizer()

        print(f"\n⚙️  정규화 중...")
        stats = normalizer.normalize_directory(input_dir, normalized_dir)

        print(f"\n✅ 문서 정규화 완료")
        print(f"─" * 50)
        print(f"  총 파일: {stats['total_files']}개")
        print(f"  성공: {stats['successful']}개")
        print(f"  실패: {stats['failed']}개")
        print(f"  미지원: {stats['unsupported']}개")
        print(f"  스킵: {stats['skipped']}개")
        print(f"  출력 디렉터리: {normalized_dir}")
        print(f"─" * 50)

        if stats['failed'] > 0:
            print(f"\n⚠️  {stats['failed']}개 파일 변환 실패:")
            for error in stats['errors']:
                print(f"   - {error['file']}: {error['error']}")

        if stats['unsupported'] > 0:
            print(f"\n⚠️  {stats['unsupported']}개 파일은 미지원 형식입니다")

    except Exception as e:
        logging.error(f"✗ 정규화 실패: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_specify(args):
    """Speckit Specify 실행"""
    workspace_dir = Path(args.run_id)

    if not workspace_dir.exists():
        print(f"✗ Workspace 없음: {workspace_dir}")
        sys.exit(1)

    print(f"\n📋 Speckit Specify 실행")
    print(f"   Run ID: {args.run_id}")
    print(f"   Workspace: {workspace_dir}")

    try:
        runner = SpeckitRunner(workspace_dir)

        # Workspace 초기화
        print(f"\n🔧 Workspace 초기화 중...")
        if not runner.initialize_workspace():
            print(f"✗ 초기화 실패")
            sys.exit(1)

        # Specify 실행
        print(f"\n📋 /speckit.specify 실행 중...")
        result = runner.run_specify()

        if result["success"]:
            print(f"\n✅ Specify 실행 완료")
            print(f"─" * 50)
            print(f"  생성된 파일: {len(result['generated_files'])}개")
            for file_path in result["generated_files"]:
                print(f"    - {Path(file_path).name}")
            print(f"─" * 50)

            # 실행 로그 저장
            runner.save_execution_log()
        else:
            print(f"✗ Specify 실행 실패: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"✗ 오류: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_plan(args):
    """Speckit Plan 실행"""
    workspace_dir = Path(args.run_id)

    if not workspace_dir.exists():
        print(f"✗ Workspace 없음: {workspace_dir}")
        sys.exit(1)

    print(f"\n📐 Speckit Plan 실행")
    print(f"   Run ID: {args.run_id}")

    try:
        runner = SpeckitRunner(workspace_dir)

        # Plan 실행
        print(f"\n📐 /speckit.plan 실행 중...")
        result = runner.run_plan()

        if result["success"]:
            print(f"\n✅ Plan 실행 완료")
            print(f"─" * 50)
            print(f"  생성된 파일: {len(result['generated_files'])}개")
            for file_path in result["generated_files"]:
                print(f"    - {Path(file_path).name}")
            print(f"─" * 50)

            # 실행 로그 저장
            runner.save_execution_log()
        else:
            print(f"✗ Plan 실행 실패: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"✗ 오류: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cmd_tasks(args):
    """Speckit Tasks 실행"""
    workspace_dir = Path(args.run_id)

    if not workspace_dir.exists():
        print(f"✗ Workspace 없음: {workspace_dir}")
        sys.exit(1)

    print(f"\n✅ Speckit Tasks 실행")
    print(f"   Run ID: {args.run_id}")

    try:
        runner = SpeckitRunner(workspace_dir)

        # Tasks 실행
        print(f"\n✅ /speckit.tasks 실행 중...")
        result = runner.run_tasks()

        if result["success"]:
            print(f"\n✅ Tasks 실행 완료")
            print(f"─" * 50)
            print(f"  생성된 파일: {len(result['generated_files'])}개")
            for file_path in result["generated_files"]:
                print(f"    - {Path(file_path).name}")
            print(f"─" * 50)

            # 실행 로그 저장
            runner.save_execution_log()
        else:
            print(f"✗ Tasks 실행 실패: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"✗ 오류: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Confluence + JIRA + SDD 문서 동기화 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # Confluence 설정
  python scripts/confluence-sync.py config --set-token "ATATT3x..."
  python scripts/confluence-sync.py status

  # Confluence 동기화
  python scripts/confluence-sync.py download              # Confluence → 로컬
  python scripts/confluence-sync.py upload                # 로컬 → Confluence
  python scripts/confluence-sync.py sync                  # 양방향 동기화

  # JIRA 설정
  python scripts/confluence-sync.py jira config --set-token "JIRA_TOKEN..."
  python scripts/confluence-sync.py jira status           # JIRA 연결 확인

  # JIRA 이슈 검색
  python scripts/confluence-sync.py jira search --status "내부검토" \\
    --document-types "요구사항정의서,유스케이스정의서"

  # SDD 워크플로우 (Phase 1-2 ~ Phase 3)
  # 1단계: 문서 수집
  python scripts/confluence-sync.py sdd collect \\
    --status "내부검토" \\
    --document-types "요구사항정의서,유스케이스정의서" \\
    --workspace "/tmp/sdd-workspaces"

  # 2단계: 문서 정규화
  python scripts/confluence-sync.py sdd normalize \\
    --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

  # 3단계: Speckit 자동화
  python scripts/confluence-sync.py sdd specify \\
    --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

  python scripts/confluence-sync.py sdd plan \\
    --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

  python scripts/confluence-sync.py sdd tasks \\
    --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"
        """
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="상세 로그 출력")

    subparsers = parser.add_subparsers(title="명령어", dest="command")

    # ===== Confluence 명령어 =====
    config_parser = subparsers.add_parser("config", help="Confluence 설정 관리")
    config_parser.add_argument("--set-token", metavar="TOKEN", help="API 토큰 저장")
    config_parser.add_argument("--show", action="store_true", help="현재 설정 표시")

    subparsers.add_parser("status", help="Confluence 동기화 상태 조회")

    dl_parser = subparsers.add_parser("download", help="Confluence → 로컬 다운로드")
    dl_parser.add_argument("--force", action="store_true", help="변경 여부 무시하고 강제 다운로드")

    ul_parser = subparsers.add_parser("upload", help="로컬 → Confluence 업로드")
    ul_parser.add_argument("--dry-run", action="store_true", help="실제 업로드 없이 대상만 표시")

    sync_parser = subparsers.add_parser("sync", help="양방향 동기화")
    conflict_group = sync_parser.add_mutually_exclusive_group()
    conflict_group.add_argument("--local-overwrite", action="store_true",
                                help="충돌 시 로컬 파일로 Confluence 덮어쓰기")
    conflict_group.add_argument("--confluence-overwrite", action="store_true",
                                help="충돌 시 Confluence 파일로 로컬 덮어쓰기")

    # ===== JIRA 명령어 =====
    jira_parser = subparsers.add_parser("jira", help="JIRA 연동 기능")
    jira_subparsers = jira_parser.add_subparsers(title="JIRA 명령어", dest="jira_command")

    jira_config_parser = jira_subparsers.add_parser("config", help="JIRA 설정 관리")
    jira_config_parser.add_argument("--set-token", metavar="TOKEN", help="API 토큰 저장")
    jira_config_parser.add_argument("--show", action="store_true", help="현재 설정 표시")

    jira_subparsers.add_parser("status", help="JIRA 연결 확인")

    jira_search_parser = jira_subparsers.add_parser("search", help="JIRA 이슈 검색")
    jira_search_parser.add_argument("--status", required=True, help="Kanban 상태 (예: 내부검토)")
    jira_search_parser.add_argument("--document-types", required=True,
                                    help="문서 유형 (쉼표 구분, 예: 요구사항정의서,유스케이스정의서)")

    # ===== SDD 명령어 =====
    sdd_parser = subparsers.add_parser("sdd", help="SDD 워크플로우")
    sdd_subparsers = sdd_parser.add_subparsers(title="SDD 명령어", dest="sdd_command")

    collect_parser = sdd_subparsers.add_parser("collect", help="JIRA 문서 수집")
    collect_parser.add_argument("--status", required=True, help="Kanban 상태")
    collect_parser.add_argument("--document-types", required=True,
                                help="문서 유형 (쉼표 구분)")
    collect_parser.add_argument("--project-key", default="GOVPJT", help="JIRA 프로젝트 키")
    collect_parser.add_argument("--workspace", default="/tmp/sdd-workspaces",
                                help="Workspace 디렉터리")

    normalize_parser = sdd_subparsers.add_parser("normalize", help="문서 정규화 (→ Markdown)")
    normalize_parser.add_argument("--run-id", required=True,
                                 help="Run ID 또는 Workspace 경로")

    specify_parser = sdd_subparsers.add_parser("specify", help="/speckit.specify 실행")
    specify_parser.add_argument("--run-id", required=True,
                               help="Run ID 또는 Workspace 경로")

    plan_parser = sdd_subparsers.add_parser("plan", help="/speckit.plan 실행")
    plan_parser.add_argument("--run-id", required=True,
                            help="Run ID 또는 Workspace 경로")

    tasks_parser = sdd_subparsers.add_parser("tasks", help="/speckit.tasks 실행")
    tasks_parser.add_argument("--run-id", required=True,
                             help="Run ID 또는 Workspace 경로")

    args = parser.parse_args()
    setup_logging(args.verbose)

    if not args.command:
        parser.print_help()
        return

    commands = {
        "config": cmd_config,
        "status": cmd_status,
        "download": cmd_download,
        "upload": cmd_upload,
        "sync": cmd_sync,
    }

    # JIRA 명령어 처리
    if args.command == "jira":
        if not args.jira_command:
            jira_parser.print_help()
            return

        if args.jira_command == "config":
            cmd_jira_config(args)
        elif args.jira_command == "status":
            cmd_jira_status(args)
        elif args.jira_command == "search":
            args.document_types = args.document_types.split(",")
            cmd_jira_search(args)
        return

    # SDD 명령어 처리
    if args.command == "sdd":
        if not args.sdd_command:
            sdd_parser.print_help()
            return

        if args.sdd_command == "collect":
            args.document_types = args.document_types.split(",")
            cmd_collect(args)
        elif args.sdd_command == "normalize":
            cmd_normalize(args)
        elif args.sdd_command == "specify":
            cmd_specify(args)
        elif args.sdd_command == "plan":
            cmd_plan(args)
        elif args.sdd_command == "tasks":
            cmd_tasks(args)
        return

    try:
        commands[args.command](args)
    except KeyboardInterrupt:
        print("\n⚠ 동기화 중단됨")
        sys.exit(1)
    except Exception as e:
        logging.error(f"✗ 오류 발생: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
