# -*- coding: utf-8 -*-
"""창고 재고 집계 파이프라인 DAG 러너.

DAG 구조:

    task_a ─┐
    task_b ─┼─▶ consolidate ─▶ result.json / report.md
    task_c ─┘

- task_a / task_b / task_c 는 서로 상호 의존성이 없는 독립 태스크다.
  따라서 세 태스크를 병렬(스레드)로 동시에 실행한다.
- 세 중간 파일(intermediate_a/b/c.json)이 모두 완료된 뒤에만
  consolidate 단계를 실행한다 (fan-in 조인).
- consolidate 는 result.json 과 report.md 를 생성한다.

실행:
    python run_dag.py
"""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# 이 스크립트 파일 기준 경로를 import 경로에 추가 (어느 CWD에서 실행해도 동작).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import task_a
import task_b
import task_c
import consolidate as consolidate_mod

# A/B/C 독립 태스크 (상호 의존 없음)
WAREHOUSE_TASKS = {
    "A": task_a.run,
    "B": task_b.run,
    "C": task_c.run,
}


def run_warehouse_tasks() -> dict:
    """A/B/C 세 집계 태스크를 병렬로 실행하고 결과 dict를 반환한다.

    세 태스크는 상호 의존성이 없으므로 ThreadPoolExecutor 로 동시에 실행한다.
    각 태스크는 자신의 intermediate_?.json 을 저장한다.

    Returns:
        창고 이름 -> 태스크 결과 dict.
    """
    results: dict = {}
    with ThreadPoolExecutor(max_workers=len(WAREHOUSE_TASKS)) as executor:
        future_to_name = {
            executor.submit(fn): name for name, fn in WAREHOUSE_TASKS.items()
        }
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            # 태스크 내부 예외가 있으면 여기서 재발생시켜 파이프라인을 멈춘다.
            results[name] = future.result()
            print(
                f"[run_dag] task_{name.lower()} 완료: "
                f"total={results[name]['total']} "
                f"items={len(results[name]['items'])} "
                f"low_stock={len(results[name]['low_stock'])}"
            )
    return results


def run() -> dict:
    """전체 DAG 파이프라인을 실행한다.

    1) A/B/C 병렬 집계 (fan-out)
    2) 세 중간 파일 완료 후 consolidate 조인 (fan-in)
    3) result.json / report.md 생성

    Returns:
        통합 결과 dict.
    """
    print("[run_dag] 1단계: A/B/C 집계 태스크 병렬 실행")
    run_warehouse_tasks()

    print("[run_dag] 2단계: 세 중간 파일 조인 후 consolidate 실행")
    result = consolidate_mod.consolidate()
    result_path = consolidate_mod.write_result(result)
    report_path = consolidate_mod.write_report(result)

    print(f"[run_dag] result.json 저장: {result_path}")
    print(f"[run_dag] report.md 저장:  {report_path}")
    print(
        f"[run_dag] grand_total={result['grand_total']} "
        f"warehouses={len(result['warehouse_totals'])} "
        f"items={len(result['item_totals'])} "
        f"low_stock={len(result['low_stock'])}"
    )
    return result


if __name__ == "__main__":
    run()
