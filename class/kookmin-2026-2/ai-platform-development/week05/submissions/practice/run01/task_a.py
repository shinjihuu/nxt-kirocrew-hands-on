# -*- coding: utf-8 -*-
"""창고 A 집계 DAG 태스크.

aggregate_warehouse.aggregate 로 practice/data/warehouse-a.md 를 집계하고
결과를 중간 파일 submissions/practice/run01/intermediate_a.json 에 저장한다.

B, C 태스크와 상호 의존성이 없는 독립 태스크다. 단독 실행 가능하다:
    python task_a.py
"""
from __future__ import annotations

import json
import os

from aggregate_warehouse import aggregate

# 이 스크립트 파일 기준 경로 계산 (어느 CWD에서 실행해도 동일하게 동작).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# run01 -> practice -> submissions -> week05
_WEEK05_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))

WAREHOUSE_NAME = "A"
SOURCE_PATH = os.path.join(_WEEK05_DIR, "practice", "data", "warehouse-a.md")
OUTPUT_PATH = os.path.join(_THIS_DIR, "intermediate_a.json")
THRESHOLD = 5


def run() -> dict:
    """창고 A를 집계해 intermediate_a.json 으로 저장하고 결과 dict를 반환한다."""
    result = aggregate(WAREHOUSE_NAME, SOURCE_PATH, threshold=THRESHOLD)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    out = run()
    print(f"[task_a] warehouse={out['warehouse']} total={out['total']} "
          f"items={len(out['items'])} low_stock={len(out['low_stock'])}")
    print(f"[task_a] wrote {OUTPUT_PATH}")
