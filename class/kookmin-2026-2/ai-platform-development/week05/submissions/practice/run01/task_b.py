# -*- coding: utf-8 -*-
"""창고 B 집계 DAG 태스크 (독립 실행 가능).

warehouse-b.md 를 aggregate_warehouse.aggregate 로 집계하고,
결과를 중간 파일 submissions/practice/run01/intermediate_b.json 에 저장한다.

A, C 태스크와 상호 의존성이 없는 독립 태스크다.
단독 실행:  python task_b.py
"""
from __future__ import annotations

import json
import os

from aggregate_warehouse import aggregate

WAREHOUSE_NAME = "B"

# 이 파일(run01) 기준으로 데이터/출력 경로를 해석해 CWD에 의존하지 않는다.
_HERE = os.path.dirname(os.path.abspath(__file__))
# run01 -> practice -> submissions -> week05
_WEEK05 = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))

WAREHOUSE_PATH = os.path.join(_WEEK05, "practice", "data", "warehouse-b.md")
OUTPUT_PATH = os.path.join(_HERE, "intermediate_b.json")


def run() -> dict:
    """창고 B를 집계해 intermediate_b.json 에 저장하고 결과 dict를 반환한다."""
    result = aggregate(WAREHOUSE_NAME, WAREHOUSE_PATH)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result


if __name__ == "__main__":
    data = run()
    print(f"[task_b] wrote {OUTPUT_PATH}")
    print(json.dumps(data, ensure_ascii=False, indent=2))
