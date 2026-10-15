# -*- coding: utf-8 -*-
"""창고 단위 재고 집계 함수 (run02).

parse_warehouse.parse() 로 읽은 [(품목, 수량)] 행 데이터를 받아
해당 창고의 총합(total)과 품목별 수량(items)을 계산한다.

run02 저재고 기준은 전체 창고 품목별 총합(item_total)이므로,
저재고 판정은 개별 창고가 아닌 merge 단계에서만 수행한다.
따라서 창고 집계 결과에는 저재고 목록을 두지 않는다.
"""
from __future__ import annotations

from typing import Dict

from parse_warehouse import parse


def aggregate(name: str, path: str) -> Dict:
    """한 창고의 재고를 집계해 dict로 반환한다.

    Args:
        name: 창고 이름 (예: "A").
        path: 창고 Markdown 파일 경로.

    Returns:
        {
            "warehouse": name,
            "total": 창고 전체 수량 합,
            "items": {품목: 수량합},  # 같은 품목 행은 합산
        }
    """
    rows = parse(path)

    total = 0
    items: Dict[str, int] = {}

    for item, qty in rows:
        total += qty
        items[item] = items.get(item, 0) + qty

    return {
        "warehouse": name,
        "total": int(total),
        "items": {k: int(v) for k, v in items.items()},
    }


if __name__ == "__main__":
    import json
    import sys

    wh_name = sys.argv[1] if len(sys.argv) > 1 else "?"
    wh_path = sys.argv[2] if len(sys.argv) > 2 else None
    if wh_path:
        print(json.dumps(aggregate(wh_name, wh_path), ensure_ascii=False, indent=2))
