#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빛담 가을사진전(E04) 주간 집계 스크립트 (단일 파일)
- data/ 의 CSV 3개(참가신청/회계내역/구매계획)를 전체 읽어 집계한다.
- 원본은 읽기 전용으로만 접근하고 수정하지 않는다.
- 집계 결과를 submissions/aggregate_week04.json 으로 저장한다.

근거 문서(지식기반):
  ACCOUNT-01 회계 집계 기준
    제1조: 기간 2026-07-01~2026-09-22, 기초 잔액 학교지원금 0 / 동아리회비 800,000
    제2조: 수입·환불입금(+), 지출·환불지급(-)
    제3조: 현재 잔액 = 기초 + 수입 + 환불입금 - 지출 - 환불지급
           E04 순지출 = 지출 + 환불지급 - 환불입금 (수입 제외)
    제5조: 구매계획 '참가자'=확정인원*계수, '고정'=계수, 비용=단가*수량
  CLUB-01 동아리 운영 규칙
    제1조: 물품 구매 기본 인원은 확정 인원
    제3조: 미전환 대기자를 확정 인원에 미리 더하지 않는다
  APPROVAL-SPACE-04 장소 사용 승인서: 승인 정원 160명
  CHANGE-SPACE-04 정원 변경 승인서(2026-09-23): 160->180명으로 변경,
    APPROVAL-SPACE-04 정원 조항을 대체 (updates/W04_09_정원변경승인서.md)
  RULE-01 학교지원금 지침: 기념품 제외(제3조), 증빙/용도 불명확 시 확인필요(제4조)
"""
import csv
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE, "..", "data"))
OUT_JSON = os.path.join(BASE, "aggregate_week04.json")

EVENT = "E04"
# ACCOUNT-01 제1조 기초 잔액
OPENING = {"학교지원금": 0, "동아리회비": 800000}
# CHANGE-SPACE-04 정원 변경 승인서로 160->180 (APPROVAL-SPACE-04 대체)
CAPACITY_APPROVED = 180
CAPACITY_ORIGINAL = 160
GRANT_LIMIT = 1500000  # APPROVAL-FUND-04 총 승인 한도


def read_csv(path):
    """utf-8-sig 우선, 실패 시 cp949/euc-kr 순서로 전체 행을 dict 리스트로 읽는다."""
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            with io.open(path, "r", encoding=enc, newline="") as f:
                rows = list(csv.DictReader(f))
            # 키/값 공백·BOM 제거
            clean = []
            for r in rows:
                clean.append({(k or "").strip().lstrip("\ufeff"): (v or "").strip()
                              for k, v in r.items()})
            return clean, enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise RuntimeError("인코딩 해석 실패: " + path)


def to_int(s):
    return int(str(s).replace(",", "").strip())


def main():
    result = {"행사": EVENT, "근거": {}, "읽은_행수": {}, "확인필요": []}

    # ---------- 1. 참가신청 ----------
    apply_path = os.path.join(DATA_DIR, "참가신청.csv")
    apply_rows, enc1 = read_csv(apply_path)
    e04_apply = [r for r in apply_rows if r.get("행사_ID") == EVENT]  # 행사 범위 한정
    result["읽은_행수"]["참가신청.csv_전체"] = len(apply_rows)
    result["읽은_행수"]["참가신청.csv_E04"] = len(e04_apply)

    status_count = {}
    for r in e04_apply:
        st = r.get("신청상태", "")
        status_count[st] = status_count.get(st, 0) + 1

    confirmed = [r for r in e04_apply if r.get("신청상태") == "확정"]
    n_confirmed = len(confirmed)
    # 확정자의 선택 집계
    inhwa_yes = sum(1 for r in confirmed if r.get("인화체험") == "신청")
    food_yes = sum(1 for r in confirmed if r.get("식음료") == "신청")

    result["참가_상태별_인원"] = status_count
    result["확정자_선택"] = {
        "확정_인원": n_confirmed,
        "인화체험_신청": inhwa_yes,
        "인화체험_미신청": n_confirmed - inhwa_yes,
        "식음료_신청": food_yes,
        "식음료_받지않음": n_confirmed - food_yes,
    }
    result["근거"]["참가"] = "CLUB-01 제1조(상태 구분), RULE-02/APPROVAL-SPACE-04(정원)"

    # ---------- 2. 회계 ----------
    acc_path = os.path.join(DATA_DIR, "회계내역.csv")
    acc_rows, enc2 = read_csv(acc_path)
    result["읽은_행수"]["회계내역.csv_전체"] = len(acc_rows)

    # 재원별 현재 잔액 (전체 행사 E01~E04 합산) — ACCOUNT-01 제3조
    balance = dict(OPENING)
    for r in acc_rows:
        fund = r.get("재원")
        typ = r.get("유형")
        amt = to_int(r.get("금액"))
        if fund not in balance:
            balance[fund] = 0
        if typ in ("수입", "환불입금"):
            balance[fund] += amt
        elif typ in ("지출", "환불지급"):
            balance[fund] -= amt
    result["현재_잔액"] = balance
    result["근거"]["현재_잔액"] = "ACCOUNT-01 제1조(기초잔액) 제2조(부호) 제3조(산식), 전체 E01~E04 합산"

    # E04 재원별 순지출 = 지출 + 환불지급 - 환불입금 (수입 제외) — ACCOUNT-01 제3조
    e04_acc = [r for r in acc_rows if r.get("행사_ID") == EVENT]
    result["읽은_행수"]["회계내역.csv_E04"] = len(e04_acc)
    net = {}
    for r in e04_acc:
        fund = r.get("재원")
        typ = r.get("유형")
        amt = to_int(r.get("금액"))
        net.setdefault(fund, 0)
        if typ in ("지출", "환불지급"):
            net[fund] += amt
        elif typ == "환불입금":
            net[fund] -= amt
        # 수입은 순지출에서 제외
    result["E04_순지출"] = net
    result["근거"]["E04_순지출"] = "ACCOUNT-01 제3조(순지출=지출+환불지급-환불입금, 수입 제외)"

    # 지원금 한도 대비 (순지출 기준) 참고
    result["학교지원금_한도대비"] = {
        "총_승인_한도": GRANT_LIMIT,
        "E04_학교지원금_순지출": net.get("학교지원금", 0),
        "비고": "APPROVAL-FUND-04. 2차 500,000은 미입금이라 가용현금 아님(RULE-01 제5조)",
    }

    # 지원금 지침 플래그 (RULE-01) — 확인필요 항목
    for r in e04_acc:
        if r.get("재원") == "학교지원금":
            item = r.get("항목", "")
            use = r.get("용도", "")
            proof = r.get("증빙", "")
            tid = r.get("거래_ID", "")
            if item == "기념품":
                result["확인필요"].append(
                    f"{tid} 기념품({use}) 학교지원금 지원 제외 대상 (RULE-01 제3조)")
            if not use:
                result["확인필요"].append(
                    f"{tid} 용도 공란 — 사용목적 확인 필요 (RULE-01 제4조)")
            if proof != "있음":
                result["확인필요"].append(
                    f"{tid} 증빙 없음 — 보류/확인 필요 (RULE-01 제4조)")

    # ---------- 3. 구매계획 ----------
    plan_path = os.path.join(DATA_DIR, "구매계획.csv")
    plan_rows, enc3 = read_csv(plan_path)
    result["읽은_행수"]["구매계획.csv_전체"] = len(plan_rows)

    def plan_for(headcount):
        """수량기준 '참가자'=headcount*계수, '고정'=계수. 비용=단가*수량. 재원별 합계."""
        by_fund = {}
        detail = []
        for r in plan_rows:
            basis = r.get("수량기준")
            coef = to_int(r.get("계수"))
            unit = to_int(r.get("단가"))
            fund = r.get("예정재원")
            if basis == "참가자":
                qty = headcount * coef
            elif basis == "고정":
                qty = coef
            else:
                qty = coef
            cost = unit * qty
            by_fund[fund] = by_fund.get(fund, 0) + cost
            detail.append({
                "항목_ID": r.get("항목_ID"), "물품": r.get("물품"),
                "수량기준": basis, "수량": qty, "단가": unit,
                "비용": cost, "예정재원": fund,
            })
        total = sum(by_fund.values())
        return {"기준인원": headcount, "재원별": by_fund, "총액": total, "상세": detail}

    # CLUB-01 제1조/제3조: 기본은 확정 인원(140). 140/160/180 시나리오.
    result["구매계획"] = {
        "확정140": plan_for(n_confirmed),      # 기본 (CLUB-01 제1조)
        "승인정원160": plan_for(CAPACITY_ORIGINAL),  # APPROVAL-SPACE-04 원안
        "변경정원180": plan_for(CAPACITY_APPROVED),  # CHANGE-SPACE-04 적용
    }
    result["근거"]["구매계획"] = (
        "ACCOUNT-01 제5조(참가자=확정*계수, 고정=계수, 비용=단가*수량), "
        "CLUB-01 제1조(기본=확정140)/제3조(대기자 선반영 금지), "
        "CHANGE-SPACE-04(정원 180 변경 승인, APPROVAL-SPACE-04 대체)")

    # 정원 근거 요약
    result["정원_근거"] = {
        "원_승인정원": CAPACITY_ORIGINAL,
        "현_승인정원": CAPACITY_APPROVED,
        "근거": "CHANGE-SPACE-04(2026-09-23)가 APPROVAL-SPACE-04의 160을 180으로 대체. "
                "지원금 증액 승인 아님, 신청상태 자동변경 아님.",
        "확정_인원": n_confirmed,
        "대기_인원": status_count.get("대기", 0),
        "비고": "확정 140명은 승인정원 180 이내. 대기자 전환은 담당자 승인 필요(CLUB-01 제3조).",
    }

    result["인코딩"] = {"참가신청": enc1, "회계내역": enc2, "구매계획": enc3}

    with io.open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 콘솔 요약
    print("읽은 행 수:", result["읽은_행수"])
    print("참가 상태별:", status_count)
    print("확정자 선택:", result["확정자_선택"])
    print("현재 잔액:", balance)
    print("E04 순지출:", net)
    for k, v in result["구매계획"].items():
        print(f"구매계획 {k}: 재원별={v['재원별']} 총액={v['총액']}")
    print("확인필요:", result["확인필요"])
    print("저장:", OUT_JSON)
    return result


if __name__ == "__main__":
    main()
