# -*- coding: utf-8 -*-
"""창고 B 집계 DAG 태스크 (run02).

aggregate_warehouse.aggregate 로 practice/data/warehouse-b.md 를 집계하고
결과를 중간 파일 submissions/practice/run02/intermediate_b.json 에 저장한다.

A, C 태스크와 상호 의존성이 없는 독립 태스크다. 단독 실행 가능하다:
    python task_b.py
"""
from __future__ import annotations

import json
import os

from aggregate_warehouse import aggregate

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_WEEK05_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))

WAREHOUSE_NAME = "B"
SOURCE_PATH = os.path.join(_WEEK05_DIR, "practice", "data", "warehouse-b.md")
OUTPUT_PATH = os.path.join(_THIS_DIR, "intermediate_b.json")


def run() -> dict:
    """창고 B를 집계해 intermediate_b.json 으로 저장하고 결과 dict를 반환한다."""
    result = aggregate(WAREHOUSE_NAME, SOURCE_PATH)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    out = run()
    print(f"[task_b] warehouse={out['warehouse']} total={out['total']} "
          f"items={len(out['items'])}")
    print(f"[task_b] wrote {OUTPUT_PATH}")
