# 창고 재고 통합 보고서 (run02)

## 적용 기준

- low_stock_basis: `item_total` (전체 창고 품목별 총수량 기준)
- threshold: `5` (품목 총수량이 이 값보다 작으면 저재고)
- 입력 파일: warehouse-a.md, warehouse-b.md, warehouse-c.md
- grand_total: **54**

## 창고별 합계

| 창고 | 합계 |
| --- | ---: |
| A | 22 |
| B | 16 |
| C | 16 |
| **합계** | **54** |

## 품목별 총수량

| 품목 | 총수량 |
| --- | ---: |
| bottle | 12 |
| cable | 1 |
| hub | 13 |
| mug | 17 |
| sensor | 11 |

## 저재고 목록

| 품목 | 총수량 |
| --- | ---: |
| cable | 1 |
