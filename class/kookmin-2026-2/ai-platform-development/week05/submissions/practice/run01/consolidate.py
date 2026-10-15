# -*- coding: utf-8 -*-
"""통합(consolidation) 단계.

intermediate_a/b/c.json 세 중간 파일을 읽어 다음을 병합한다:
  - warehouse_totals: 창고 이름 -> 정수 총합
  - item_totals: 품목 이름 -> 전체 창고 정수 합계
  - grand_total: 전체 수량
  - low_stock: 통합 저재고 목록 (각 항목에 item/quantity/warehouse 포함)

출력형식.md 구조에 맞춰 source_files, warehouse_totals, item_totals,
grand_total, low_stock_basis='warehouse_row', threshold=5, low_stock 필드를
구성한다. 모든 수치는 정수로 저장한다.

저재고 기준(low_stock_basis)은 창고별 원본 '행' 수량 기준(warehouse_row)이다.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

# 이 스크립트 파일 기준 경로 계산 (어느 CWD에서 실행해도 동일하게 동작).
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# 중간 파일 경로 (창고 이름 -> 파일 경로)
INTERMEDIATE_FILES = {
    "A": os.path.join(_THIS_DIR, "intermediate_a.json"),
    "B": os.path.join(_THIS_DIR, "intermediate_b.json"),
    "C": os.path.join(_THIS_DIR, "intermediate_c.json"),
}

# 입력 원본 파일 이름 (출력형식.md의 source_files 용)
SOURCE_FILES = ["warehouse-a.md", "warehouse-b.md", "warehouse-c.md"]

THRESHOLD = 5
LOW_STOCK_BASIS = "warehouse_row"

# 통합 결과 저장 경로
RESULT_PATH = os.path.join(_THIS_DIR, "result.json")

# Markdown 보고서 저장 경로
REPORT_PATH = os.path.join(_THIS_DIR, "report.md")


def _load_intermediate(path: str) -> Dict:
    """중간 JSON 파일 하나를 읽어 dict로 반환한다."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def consolidate(intermediate_files: Dict[str, str] = INTERMEDIATE_FILES) -> Dict:
    """세 중간 파일을 병합해 통합 결과 dict를 반환한다.

    Args:
        intermediate_files: 창고 이름 -> 중간 JSON 파일 경로.

    Returns:
        출력형식.md 구조를 따르는 통합 결과 dict.
    """
    warehouse_totals: Dict[str, int] = {}
    item_totals: Dict[str, int] = {}
    low_stock: List[Dict] = []
    grand_total = 0

    # 창고 이름 순서를 안정적으로 유지 (A, B, C ...)
    for name in sorted(intermediate_files):
        data = _load_intermediate(intermediate_files[name])

        wh_total = int(data["total"])
        warehouse_totals[name] = wh_total
        grand_total += wh_total

        # 품목별 전체 합계 누적
        for item, qty in data["items"].items():
            item_totals[item] = item_totals.get(item, 0) + int(qty)

        # 통합 저재고 목록 (창고별 행 기준) 병합
        for entry in data["low_stock"]:
            low_stock.append(
                {
                    "item": entry["item"],
                    "quantity": int(entry["quantity"]),
                    "warehouse": entry.get("warehouse", name),
                }
            )

    return {
        "source_files": list(SOURCE_FILES),
        "warehouse_totals": warehouse_totals,
        "item_totals": item_totals,
        "grand_total": int(grand_total),
        "low_stock_basis": LOW_STOCK_BASIS,
        "threshold": int(THRESHOLD),
        "low_stock": low_stock,
    }


def write_result(result: Dict, path: str = RESULT_PATH) -> str:
    """통합 결과 dict를 result.json으로 저장한다.

    ensure_ascii=False, indent=2로 저장하여 한글이 그대로 보이게 한다.
    low_stock_basis는 반드시 'warehouse_row'로 기록한다.

    Args:
        result: consolidate()가 반환한 통합 결과 dict.
        path: 저장할 result.json 경로.

    Returns:
        저장한 파일의 경로.
    """
    # 기준값 보증: 1차 결과는 창고별 행 기준(warehouse_row)으로 기록한다.
    result["low_stock_basis"] = LOW_STOCK_BASIS

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return path


def write_report(result: Dict, path: str = REPORT_PATH) -> str:
    """통합 결과 dict를 바탕으로 Markdown 보고서(report.md)를 생성한다.

    result.json과 동일한 수치를 담으며 다음을 포함한다:
      - 창고별 합계 표 (warehouse_totals)
      - 품목별 합계 표 (item_totals)
      - 저재고 목록 (low_stock)
      - 적용 기준 (low_stock_basis, threshold)

    Args:
        result: consolidate()가 반환한 통합 결과 dict.
        path: 저장할 report.md 경로.

    Returns:
        저장한 파일의 경로.
    """
    lines: List[str] = []
    lines.append("# 창고 재고 통합 보고서")
    lines.append("")

    # 적용 기준
    lines.append("## 적용 기준")
    lines.append("")
    lines.append(f"- low_stock_basis: `{result['low_stock_basis']}` (창고별 원본 행 수량 기준)")
    lines.append(f"- threshold: `{result['threshold']}` (수량이 이 값보다 작으면 저재고)")
    lines.append(f"- 입력 파일: {', '.join(result['source_files'])}")
    lines.append(f"- grand_total: **{result['grand_total']}**")
    lines.append("")

    # 창고별 합계 표
    lines.append("## 창고별 합계")
    lines.append("")
    lines.append("| 창고 | 합계 |")
    lines.append("| --- | ---: |")
    for name in sorted(result["warehouse_totals"]):
        lines.append(f"| {name} | {result['warehouse_totals'][name]} |")
    lines.append(f"| **합계** | **{result['grand_total']}** |")
    lines.append("")

    # 품목별 합계 표
    lines.append("## 품목별 합계")
    lines.append("")
    lines.append("| 품목 | 수량 |")
    lines.append("| --- | ---: |")
    for item in sorted(result["item_totals"]):
        lines.append(f"| {item} | {result['item_totals'][item]} |")
    lines.append("")

    # 저재고 목록
    lines.append("## 저재고 목록")
    lines.append("")
    if result["low_stock"]:
        lines.append("| 품목 | 수량 | 창고 |")
        lines.append("| --- | ---: | --- |")
        for entry in result["low_stock"]:
            lines.append(
                f"| {entry['item']} | {entry['quantity']} | {entry.get('warehouse', '')} |"
            )
    else:
        lines.append("저재고 품목이 없습니다.")
    lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


if __name__ == "__main__":
    result = consolidate()
    out_path = write_result(result)
    report_path = write_report(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[저장 완료] {out_path}")
    print(f"[저장 완료] {report_path}")
