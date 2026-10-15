# 창고 재고 통합 보고서

## 적용 기준

- low_stock_basis: `warehouse_row` (창고별 원본 행 수량 기준)
- threshold: `5` (수량이 이 값보다 작으면 저재고)
- 입력 파일: warehouse-a.md, warehouse-b.md, warehouse-c.md
- grand_total: **54**

## 창고별 합계

| 창고 | 합계 |
| --- | ---: |
| A | 22 |
| B | 16 |
| C | 16 |
| **합계** | **54** |

## 품목별 합계

| 품목 | 수량 |
| --- | ---: |
| bottle | 12 |
| cable | 1 |
| hub | 13 |
| mug | 17 |
| sensor | 11 |

## 저재고 목록

| 품목 | 수량 | 창고 |
| --- | ---: | --- |
| bottle | 3 | A |
| hub | 2 | B |
| sensor | 4 | C |
| cable | 1 | C |
