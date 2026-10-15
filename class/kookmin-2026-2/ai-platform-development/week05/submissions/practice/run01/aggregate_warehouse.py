# -*- coding: utf-8 -*-
"""창고 단위 재고 집계 함수.

parse_warehouse.parse() 로 읽은 [(품목, 수량)] 행 데이터를 받아
해당 창고의 총합(total), 품목별 수량(items), 저재고 목록(low_stock)을 계산한다.

저재고 기준(low_stock_basis)은 warehouse_row:
각 창고 원본 '행'의 수량이 threshold(기본 5) 미만인 품목을 저재고로 본다.
동일 품목이 한 창고에 여러 행으로 나타나면 각 행을 개별 판정한다.
"""
from __future__ import annotations

from typing import Dict, List

from parse_warehouse import parse


def aggregate(name: str, path: str, threshold: int = 5) -> Dict:
    """한 창고의 재고를 집계해 dict로 반환한다.

    Args:
        name: 창고 이름 (예: "A").
        path: 창고 Markdown 파일 경로.
        threshold: 저재고 판정 기준 수량 (이 값 미만이면 저재고).

    Returns:
        {
            "warehouse": name,
            "total": 창고 전체 수량 합,
            "items": {품목: 수량합}  # 같은 품목 행은 합산
            "low_stock": [            # 창고 행 수량 < threshold 인 행들
                {"item": 품목, "quantity": 행수량, "warehouse": name},
                ...
            ],
            "threshold": threshold,
            "low_stock_basis": "warehouse_row",
        }
    """
    rows = parse(path)

    total = 0
    items: Dict[str, int] = {}
    low_stock: List[Dict] = []

    for item, qty in rows:
        total += qty
        items[item] = items.get(item, 0) + qty
        # 저재고 판정은 '창고 행' 수량 기준 (warehouse_row)
        if qty < threshold:
            low_stock.append(
                {"item": item, "quantity": qty, "warehouse": name}
            )

    return {
        "warehouse": name,
        "total": total,
        "items": items,
        "low_stock": low_stock,
        "threshold": threshold,
        "low_stock_basis": "warehouse_row",
    }


if __name__ == "__main__":
    import json
    import sys

    wh_name = sys.argv[1] if len(sys.argv) > 1 else "?"
    wh_path = sys.argv[2] if len(sys.argv) > 2 else None
    if wh_path:
        result = aggregate(wh_name, wh_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
