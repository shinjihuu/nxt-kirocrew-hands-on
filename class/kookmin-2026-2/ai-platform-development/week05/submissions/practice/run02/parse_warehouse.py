# -*- coding: utf-8 -*-
"""창고 재고 Markdown 표 파서 유틸 (run02).

practice/data/warehouse-*.md 의 Markdown 표(| 품목 | 수량 |)를 읽어
[(품목, 정수수량)] 리스트로 반환한다. 세 집계 태스크(task_a/b/c)가 공유한다.
"""
from __future__ import annotations

import re
from typing import List, Tuple


def _split_row(line: str) -> List[str]:
    """Markdown 표 한 줄을 셀 리스트로 분해한다 (양끝 파이프/공백 제거)."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _is_separator(cells: List[str]) -> bool:
    """|---|---:| 같은 구분선 행인지 판별한다."""
    if not cells:
        return False
    return all(re.fullmatch(r":?-{1,}:?", c) is not None for c in cells if c != "")


def parse(path: str) -> List[Tuple[str, int]]:
    """주어진 창고 Markdown 파일을 읽어 [(품목, 정수수량)] 리스트로 반환한다.

    - 표가 아닌 줄(제목 등)과 헤더/구분선 행은 건너뛴다.
    - 수량은 정수로 변환한다 (천단위 콤마 허용).
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    rows: List[Tuple[str, int]] = []
    header_seen = False

    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = _split_row(line)
        if len(cells) < 2:
            continue

        if _is_separator(cells):
            continue

        item, qty_raw = cells[0], cells[1]

        # 헤더 행(| 품목 | 수량 |) 건너뛰기
        if not header_seen:
            header_seen = True
            if not re.fullmatch(r"-?\d[\d,]*", qty_raw):
                continue

        if not item:
            continue

        qty_clean = qty_raw.replace(",", "")
        try:
            qty = int(qty_clean)
        except ValueError:
            continue

        rows.append((item, qty))

    return rows


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        for name, quantity in parse(target):
            print(f"{name}\t{quantity}")
