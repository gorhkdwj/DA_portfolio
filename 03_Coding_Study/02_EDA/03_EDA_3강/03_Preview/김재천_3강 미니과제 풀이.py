## 김재천_3강 미니과제 풀이

import pandas as pd
import numpy as np


raw = [
    {
        "order_id": "O001",
        "date": "2026-01-01 09:12",
        "store": "광교점",
        "menu": "Americano",
        "price": "4,500원",
        "qty": "2",
        "paid": "TRUE",
        "channel": "kiosk",
    },
    {
        "order_id": "O002",
        "date": "2026/01/01 10:05",
        "store": "광교점",
        "menu": " Latte ",
        "price": "5000",
        "qty": 1,
        "paid": "True",
        "channel": "app",
    },
    {
        "order_id": "O003",
        "date": "2026-01-02 12:20",
        "store": "광교점",
        "menu": "Mocha",
        "price": None,
        "qty": 2,
        "paid": "FALSE",
        "channel": "kiosk",
    },
    {
        "order_id": "O004",
        "date": "2026-01-03 15:40",
        "store": "수원점",
        "menu": "Americano",
        "price": "4500",
        "qty": None,
        "paid": True,
        "channel": "app",
    },
    {
        "order_id": "O005",
        "date": "2026-01-03 18:10",
        "store": "수원점",
        "menu": "latte",
        "price": "5,000원",
        "qty": "3",
        "paid": "TRUE",
        "channel": "kiosk",
    },
    {
        "order_id": "O006",
        "date": "2026-01-04 08:55",
        "store": "수원점",
        "menu": "Vanilla Latte",
        "price": "5800원",
        "qty": "1",
        "paid": "TRUE",
        "channel": "app",
    },
    {
        "order_id": "O007",
        "date": "2026-01-04 09:10",
        "store": "광교점",
        "menu": "Mocha",
        "price": "5500",
        "qty": "1",
        "paid": "FALSE",
        "channel": "kiosk",
    },
    {
        "order_id": "O008",
        "date": "2026-01-05 11:00",
        "store": "광교점",
        "menu": "Americano",
        "price": "4500원",
        "qty": "1",
        "paid": "TRUE",
        "channel": "app",
    },
]

df = pd.DataFrame(raw)

# date 전처리
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day_name"] = df["date"].dt.day_name()  # 요일(영문)
df["ym"] = df["date"].dt.to_period("M").astype(str)  # "2026-01" 형태

# menu 전처리
df["menu"] = df["menu"].astype(str).str.strip().str.title()

# price 전처리
df["price"] = df["price"].astype(str).str.replace("원", "").str.replace(",", "")
df["price"] = pd.to_numeric(df["price"], errors="coerce")

# qty 전처리
df["qty"] = pd.to_numeric(df["qty"], errors="coerce")  # 결측치 찾아서
df["qty"] = df["qty"].fillna(1)  # 결측치 제거한 '뒤에'
df["qty"] = df["qty"].astype(int)  # 정수형 변환


# paid 전처리
def to_bool(x):
    if isinstance(x, bool):
        return x
    x = str(x).strip().lower()
    return x in ["true", "1", "yes", "y"]


df["paid"] = df["paid"].apply(to_bool)

# sales
df["sales"] = np.where(df["paid"], df["price"] * df["qty"], 0)

# menu_map merge
menu_map = pd.DataFrame(
    [
        {"menu": "Americano", "category": "Coffee"},
        {"menu": "Latte", "category": "Coffee"},
        {"menu": "Mocha", "category": "Coffee"},
        {"menu": "Vanilla Latte", "category": "Latte Variations"},
    ]
)

df2 = df.merge(menu_map, on="menu", how="left")

# channel_kr 추가
channel_map = {"kiosk": "키오스크", "app": "앱"}
df2["channel_kr"] = df2["channel"].map(channel_map).fillna("기타")

# summary_A
summary_A = (
    df2.groupby(["ym", "day_name"])
    .agg(total_sales=("sales", "sum"), paid_rate=("paid", "mean"))
    .reset_index()
)

summary_A_pivot = summary_A.pivot(
    index="ym", columns="day_name", values="total_sales"
).fillna(0)

# summary_B
summary_B = (
    df2.groupby(["category", "menu"])
    .agg(
        total_sales=("sales", "sum"),
        total_qty=("qty", "sum"),
        orders=("order_id", "count"),
        paid_rate=("paid", "mean"),
    )
    .reset_index()
)

summary_B = summary_B.sort_values("total_sales", ascending=False).reset_index()

# 파일 저장
import os

os.makedirs("data", exist_ok=True)

summary_A.to_csv("data/summary_A_long.csv", index=False)
summary_A_pivot.to_csv("data/summary_A_pivot.csv")
summary_B.to_csv("data/summary_B_menu.csv", index=False)

check_long = pd.read_csv("data/summary_A_long.csv")
check_pivot = pd.read_csv("data/summary_A_pivot.csv")
check_menu = pd.read_csv("data/summary_B_menu.csv")

# check_long
# check_pivot
# check_menu
