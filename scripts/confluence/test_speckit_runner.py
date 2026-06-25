"""Speckit Runner 테스트"""

import sys
import logging
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from speckit_runner import SpeckitRunner

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_initialization():
    """Workspace 초기화 테스트"""
    print("\n" + "="*60)
    print("1. Workspace 초기화 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "test-workspace"

            runner = SpeckitRunner(workspace_dir)
            success = runner.initialize_workspace()

            if success:
                print(f"\n✅ Workspace 초기화 성공")
                print(f"   경로: {workspace_dir}")
                print(f"   디렉터리:")
                print(f"     - .specify/")
                print(f"     - specs/")

                # 생성된 파일 확인
                config_file = workspace_dir / ".specify" / "config.json"
                if config_file.exists():
                    print(f"   ✓ config.json 생성됨")

                return True
            else:
                print(f"❌ 초기화 실패")
                return False

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specify_workflow():
    """Specify 워크플로우 테스트"""
    print("\n" + "="*60)
    print("2. Specify 워크플로우 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "test-workspace"

            runner = SpeckitRunner(workspace_dir)

            # 초기화
            runner.initialize_workspace()

            # 입력 파일 생성 (모의)
            input_dir = workspace_dir / "input"
            input_dir.mkdir(parents=True, exist_ok=True)

            test_input = input_dir / "test.md"
            test_input.write_text("# 테스트 문서\n\n요구사항 1\n요구사항 2", encoding='utf-8')

            # Specify 실행
            print(f"\n📋 /speckit.specify 실행 중...")
            result = runner.run_specify()

            if result["success"]:
                print(f"✅ Specify 실행 성공")
                print(f"   생성된 파일: {len(result['generated_files'])}개")

                for file_path in result["generated_files"]:
                    file_name = Path(file_path).name
                    print(f"     - {file_name}")

                return True
            else:
                print(f"❌ Specify 실행 실패: {result.get('error')}")
                return False

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plan_workflow():
    """Plan 워크플로우 테스트"""
    print("\n" + "="*60)
    print("3. Plan 워크플로우 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "test-workspace"

            runner = SpeckitRunner(workspace_dir)

            # 초기화
            runner.initialize_workspace()

            # Specify 결과물 생성 (모의)
            specs_dir = workspace_dir / "specs"
            specs_dir.mkdir(parents=True, exist_ok=True)

            (specs_dir / "requirements.md").write_text("# 요구사항\n\nREQ-001\nREQ-002", encoding='utf-8')
            (specs_dir / "spec.md").write_text("# 명세\n\n명세 내용", encoding='utf-8')

            # Plan 실행
            print(f"\n📐 /speckit.plan 실행 중...")
            result = runner.run_plan()

            if result["success"]:
                print(f"✅ Plan 실행 성공")
                print(f"   생성된 파일: {len(result['generated_files'])}개")

                for file_path in result["generated_files"]:
                    file_name = Path(file_path).name
                    print(f"     - {file_name}")

                return True
            else:
                print(f"❌ Plan 실행 실패: {result.get('error')}")
                return False

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tasks_workflow():
    """Tasks 워크플로우 테스트"""
    print("\n" + "="*60)
    print("4. Tasks 워크플로우 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "test-workspace"

            runner = SpeckitRunner(workspace_dir)

            # 초기화
            runner.initialize_workspace()

            # Plan 결과물 생성 (모의)
            specs_dir = workspace_dir / "specs"
            specs_dir.mkdir(parents=True, exist_ok=True)

            (specs_dir / "spec.md").write_text("# 명세", encoding='utf-8')
            (specs_dir / "plan.md").write_text("# 계획", encoding='utf-8')
            (specs_dir / "component_spec.md").write_text("# 컴포넌트", encoding='utf-8')

            # Tasks 실행
            print(f"\n✅ /speckit.tasks 실행 중...")
            result = runner.run_tasks()

            if result["success"]:
                print(f"✅ Tasks 실행 성공")
                print(f"   생성된 파일: {len(result['generated_files'])}개")

                for file_path in result["generated_files"]:
                    file_name = Path(file_path).name
                    print(f"     - {file_name}")

                return True
            else:
                print(f"❌ Tasks 실행 실패: {result.get('error')}")
                return False

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_execution_log():
    """실행 로그 테스트"""
    print("\n" + "="*60)
    print("5. 실행 로그 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "test-workspace"

            runner = SpeckitRunner(workspace_dir)

            # 여러 단계 실행
            runner.initialize_workspace()
            runner.run_specify()
            runner.run_plan()

            # 로그 확인
            log = runner.get_execution_log()

            print(f"\n✅ 실행 로그 생성 완료: {len(log)}개 항목")
            for entry in log:
                step = entry.get("step", "unknown")
                status = entry.get("status", "unknown")
                print(f"   - {step}: {status}")

            # 로그 저장
            log_file = runner.save_execution_log()
            print(f"\n✓ 로그 저장됨: {log_file}")

            return True

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 테스트 실행"""
    print("\n")
    print("█" * 60)
    print("█  Speckit Runner 테스트")
    print("█" * 60)

    results = {
        "Workspace 초기화": test_initialization(),
        "Specify 워크플로우": test_specify_workflow(),
        "Plan 워크플로우": test_plan_workflow(),
        "Tasks 워크플로우": test_tasks_workflow(),
        "실행 로그": test_execution_log(),
    }

    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\n총 {total}개 중 {passed}개 통과")

    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
