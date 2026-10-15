# run02

이 디렉터리는 week05 창고 재고 집계 과제의 2차(run02) 산출물 디렉터리입니다.

## DAG 구조

```
task_a ─┐
task_b ─┼─▶ consolidate(merge) ─▶ result.json / report.md
task_c ─┘
```

- `task_a.py` / `task_b.py` / `task_c.py`: 창고 A·B·C를 각각 집계하는 **상호 의존 없는 독립 태스크**. 각자 `intermediate_a/b/c.json`을 생성한다. 단독 실행 가능.
- `consolidate.py`: 세 중간 파일이 모두 완료된 뒤 실행되는 **merge 태스크**(fan-in). 품목별 총수량을 계산하고, 전체 품목 총수량이 5 미만인 품목을 저재고로 판정(`low_stock_basis=item_total`, `threshold=5`)하여 `result.json`과 `report.md`를 작성한다.
- `run_dag.py`: DAG 러너. A/B/C를 병렬 실행(fan-out)한 뒤 merge로 조인(fan-in)한다.
- `parse_warehouse.py` / `aggregate_warehouse.py`: 공용 파서·집계 유틸.

## 실행

```
python run_dag.py
```

## run01과의 차이

run01은 창고별 원본 행 기준(`low_stock_basis=warehouse_row`)으로 저재고를 판정했고,
run02는 전체 창고 품목별 총수량 기준(`low_stock_basis=item_total`)으로 판정한다.
