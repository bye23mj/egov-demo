#!/usr/bin/env python3
"""
Phase 4: 계획 수립 (Planning)
요구사항 기반 구현 계획, 태스크 분류, 예상 일정 계산
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

def create_tasks_from_requirements(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """요구사항에서 태스크 생성"""
    tasks = []
    task_id = 1
    
    for req in spec["requirements"]:
        # 기본 태스크
        base_task = {
            "taskId": f"TASK-{req['req_id']}",
            "requirement": req["req_id"],
            "title": req["description"],
            "type": "DEVELOPMENT",
            "priority": req["priority"],
            "estimated_hours": estimate_effort(req),
            "subtasks": [],
        }
        
        # 요구사항 유형별 서브태스크 생성
        if req["type"] == "FUNCTIONAL":
            base_task["subtasks"] = [
                {
                    "id": f"TASK-{req['req_id']}-1",
                    "title": "설계 및 아키텍처 검토",
                    "type": "DESIGN",
                    "estimated_hours": 4,
                },
                {
                    "id": f"TASK-{req['req_id']}-2",
                    "title": "코드 구현",
                    "type": "DEVELOPMENT",
                    "estimated_hours": 8,
                },
                {
                    "id": f"TASK-{req['req_id']}-3",
                    "title": "단위 테스트 작성 및 실행",
                    "type": "TESTING",
                    "estimated_hours": 4,
                },
            ]
        elif req["type"] == "SECURITY":
            base_task["subtasks"] = [
                {
                    "id": f"TASK-{req['req_id']}-1",
                    "title": "보안 정책 검토",
                    "type": "ANALYSIS",
                    "estimated_hours": 3,
                },
                {
                    "id": f"TASK-{req['req_id']}-2",
                    "title": "보안 기능 구현",
                    "type": "DEVELOPMENT",
                    "estimated_hours": 6,
                },
                {
                    "id": f"TASK-{req['req_id']}-3",
                    "title": "보안 테스트 및 검증",
                    "type": "TESTING",
                    "estimated_hours": 4,
                },
            ]
        elif req["type"] == "INTEGRATION":
            base_task["subtasks"] = [
                {
                    "id": f"TASK-{req['req_id']}-1",
                    "title": "외부 시스템 API 분석",
                    "type": "ANALYSIS",
                    "estimated_hours": 3,
                },
                {
                    "id": f"TASK-{req['req_id']}-2",
                    "title": "연계 인터페이스 구현",
                    "type": "DEVELOPMENT",
                    "estimated_hours": 8,
                },
                {
                    "id": f"TASK-{req['req_id']}-3",
                    "title": "통합 테스트",
                    "type": "TESTING",
                    "estimated_hours": 5,
                },
            ]
        
        # 모든 태스크에 공통 태스크 추가
        base_task["subtasks"].extend([
            {
                "id": f"TASK-{req['req_id']}-REVIEW",
                "title": "코드 리뷰",
                "type": "QA",
                "estimated_hours": 2,
            },
            {
                "id": f"TASK-{req['req_id']}-DOC",
                "title": "문서 작성",
                "type": "DOCUMENTATION",
                "estimated_hours": 2,
            },
        ])
        
        # 총 추정 시간 재계산
        base_task["estimated_hours"] = sum(st["estimated_hours"] for st in base_task["subtasks"])
        
        tasks.append(base_task)
    
    return tasks

def estimate_effort(requirement: Dict[str, Any]) -> int:
    """요구사항의 예상 노력 시간 계산"""
    hours = 12  # 기본값
    
    # 우선순위에 따른 조정
    priority_multiplier = {
        "HIGH": 1.2,
        "MEDIUM": 1.0,
        "LOW": 0.8,
    }
    
    hours = int(hours * priority_multiplier.get(requirement.get("priority", "MEDIUM"), 1.0))
    return hours

def create_project_timeline(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """프로젝트 일정 생성"""
    start_date = datetime.now()
    total_hours = sum(t["estimated_hours"] for t in tasks)
    
    # 평균 개발자 생산성: 6시간/일
    total_days = total_hours / 6
    end_date = start_date + timedelta(days=total_days)
    
    # 주차별 계획
    weeks = []
    current_date = start_date
    remaining_tasks = list(tasks)
    
    for week_num in range(1, int(total_days / 7) + 2):
        week_end = current_date + timedelta(days=7)
        week_tasks = []
        week_hours = 0
        
        for task in remaining_tasks[:2]:  # 주당 2개 태스크
            if week_hours + task["estimated_hours"] <= 30:  # 주당 최대 30시간
                week_tasks.append(task["taskId"])
                week_hours += task["estimated_hours"]
                remaining_tasks.remove(task)
        
        if week_tasks:
            weeks.append({
                "week": week_num,
                "start_date": current_date.isoformat(),
                "end_date": week_end.isoformat(),
                "tasks": week_tasks,
                "estimated_hours": week_hours,
            })
        
        current_date = week_end
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_days": int(total_days),
        "total_hours": total_hours,
        "weeks": weeks,
    }

def main():
    print("\n" + "="*70)
    print("📅 Phase 4: 계획 수립 (Planning)")
    print("="*70)
    
    # 작업 디렉토리
    workspace = Path("/Users/ai/vscode/egov-demo/docs/00. confluence")
    spec_file = workspace / "specification.json"
    
    if not spec_file.exists():
        print(f"✗ specification.json을 찾을 수 없습니다")
        sys.exit(1)
    
    # 스펙 로드
    with open(spec_file) as f:
        spec_data = json.load(f)
    
    print(f"\n✓ Step 1: 태스크 생성")
    
    all_tasks = []
    for spec in spec_data["specifications"]:
        print(f"\n  분석 중: {spec['sourceDocument']['title']}")
        
        tasks = create_tasks_from_requirements(spec)
        all_tasks.extend(tasks)
        
        print(f"    - 태스크: {len(tasks)}개")
        for task in tasks:
            print(f"      • {task['taskId']}: {task['estimated_hours']}시간")
    
    print(f"\n✓ Step 2: 프로젝트 일정 계획")
    
    timeline = create_project_timeline(all_tasks)
    
    print(f"\n  계획 기간:")
    print(f"    - 시작: {timeline['start_date']}")
    print(f"    - 종료: {timeline['end_date']}")
    print(f"    - 총 기간: {timeline['total_days']}일")
    print(f"    - 총 노력: {timeline['total_hours']}시간")
    print(f"    - 주차: {len(timeline['weeks'])}주")
    
    print(f"\n  주차별 계획:")
    for week in timeline["weeks"]:
        print(f"    Week {week['week']}: {len(week['tasks'])}개 태스크, {week['estimated_hours']}시간")
    
    # 계획 저장
    print(f"\n✓ Step 3: 계획 저장")
    
    planning_output = {
        "runId": spec_data["runId"],
        "phase": "4-planning",
        "generatedAt": datetime.now().isoformat(),
        "statistics": {
            "total_tasks": len(all_tasks),
            "total_subtasks": sum(len(t["subtasks"]) for t in all_tasks),
            "total_hours": timeline["total_hours"],
            "total_days": timeline["total_days"],
        },
        "tasks": all_tasks,
        "timeline": timeline,
        "risk_factors": [
            "문서 품질이 중간 수준(60점) - 추가 요구사항 분석 필요",
            "외부 시스템 연계 요구사항 - 타 팀과의 조율 필요",
            "보안 요구사항 - 보안 전문가 검토 필요",
        ],
    }
    
    planning_file = workspace / "planning.json"
    with open(planning_file, 'w', encoding='utf-8') as f:
        json.dump(planning_output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 저장: {planning_file}")
    
    # 마크다운 형식 계획도 생성
    print(f"\n✓ Step 4: 마크다운 계획 생성")
    
    planning_md = f"""# 프로젝트 계획

## 개요
- **기간**: {timeline['start_date']} ~ {timeline['end_date']}
- **예상 기간**: {timeline['total_days']}일
- **총 노력**: {timeline['total_hours']}시간
- **팀 규모**: 1명 (평균 6시간/일 기준)

## 태스크 요약
- **총 태스크**: {len(all_tasks)}개
- **총 서브태스크**: {planning_output['statistics']['total_subtasks']}개

## 주차별 일정

"""
    
    for week in timeline["weeks"]:
        planning_md += f"""### Week {week['week']} ({week['start_date']} ~ {week['end_date']})
- 태스크: {', '.join(week['tasks'])}
- 예상 시간: {week['estimated_hours']}시간

"""
    
    planning_md += """## 위험 요소 (Risk Factors)

"""
    for i, risk in enumerate(planning_output.get("risk_factors", []), 1):
        planning_md += f"- {risk}\n"
    
    planning_md += """

## 다음 단계
- [ ] 팀 미팅: 계획 검토 및 승인
- [ ] 리소스 할당
- [ ] 세부 설계 시작
- [ ] 개발 진행

"""
    
    planning_md_file = workspace / "PLANNING.md"
    planning_md_file.write_text(planning_md, encoding='utf-8')
    print(f"  ✓ {planning_md_file.name}")
    
    # 결과 요약
    print(f"\n" + "="*70)
    print(f"✅ 계획 수립 완료!")
    print(f"="*70)
    
    print(f"\n📊 계획 요약:")
    print(f"  태스크: {len(all_tasks)}개")
    print(f"  서브태스크: {planning_output['statistics']['total_subtasks']}개")
    print(f"  총 노력: {timeline['total_hours']}시간 ({timeline['total_days']}일)")
    print(f"  주차: {len(timeline['weeks'])}주")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
