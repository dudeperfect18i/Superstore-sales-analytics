import pandas as pd
import numpy as np
import os

CLEANED_PATH = "cleaned_data.csv"  
def load():
    return pd.read_csv(CLEANED_PATH, parse_dates=["order_date", "ship_date"])

def summary_stats(df):
    print("═" * 50)
    print("SUMMARY STATISTICS")
    print("═" * 50)
    print(f"Total orders      : {len(df):,}")
    print(f"Date range        : {df['order_date'].min().date()} → {df['order_date'].max().date()}")
    print(f"Total revenue     : ₹{df['sales'].sum():,.0f}")
    print(f"Total profit      : ₹{df['profit'].sum():,.0f}")
    print(f"Avg profit margin : {df['profit_margin_pct'].mean():.1f}%")
    print(f"Loss-making orders: {df['is_loss'].sum():,} ({df['is_loss'].mean()*100:.1f}%)")
    print(f"Avg shipping days : {df['shipping_days'].mean():.1f} days")

def category_analysis(df):
    print("\n═" * 50)
    print("REVENUE & PROFIT BY CATEGORY")
    print("═" * 50)
    cat = df.groupby("category").agg(
        revenue   = ("sales",  "sum"),
        profit    = ("profit", "sum"),
        orders    = ("sales",  "count"),
        avg_margin= ("profit_margin_pct", "mean")
    ).round(2).sort_values("revenue", ascending=False)
    print(cat.to_string())
    print("\n KEY INSIGHT: Technology = high margin, Furniture = low/negative")

def discount_damage(df):
    print("\n═" * 50)
    print("DISCOUNT vs PROFIT MARGIN — HEADLINE FINDING")
    print("═" * 50)
    df["discount_bucket"] = pd.cut(
        df["discount"],
        bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
        labels=["0%", "1-10%", "11-20%", "21-30%", "31-50%", "50%+"]
    )
    result = df.groupby("discount_bucket", observed=True).agg(
        avg_margin = ("profit_margin_pct", "mean"),
        orders     = ("sales", "count")
    ).round(2)
    print(result.to_string())
    print("\n  YOUR HEADLINE: Higher discount = lower/negative margin")

def top_and_bottom(df):
    print("\n═" * 50)
    print("TOP 5 MOST PROFITABLE SUB-CATEGORIES")
    print("═" * 50)
    sub = df.groupby("sub-category")["profit"].sum().sort_values(ascending=False)
    print(sub.head(5).to_string())

    print("\n═" * 50)
    print("BOTTOM 5 (LOSS-MAKING) SUB-CATEGORIES")
    print("═" * 50)
    print(sub.tail(5).to_string())
    print("\n Tables usually shows big losses — ACTIONABLE finding!")

def regional_view(df):
    print("\n═" * 50)
    print("REVENUE BY REGION")
    print("═" * 50)
    region = df.groupby("region").agg(
        revenue=("sales", "sum"),
        profit =("profit", "sum")
    ).round(0)
    print(region.to_string())

def save_insights(df):
    os.makedirs("outputs", exist_ok=True)
    lines = [
        " KEY INSIGHTS — RETAIL SALES ANALYSIS",
        "=" * 50,
        f"Total revenue: ₹{df['sales'].sum():,.0f}",
        f"Total profit: ₹{df['profit'].sum():,.0f}",
        f"Overall margin: {df['profit'].sum()/df['sales'].sum()*100:.1f}%",
        f"Loss orders: {df['is_loss'].sum()} ({df['is_loss'].mean()*100:.1f}%)",
        "",
        " YOUR FINDINGS (fill after running):",
        "1. [Discount vs Margin correlation]",
        "2. [Worst performing category/sub-category]", 
        "3. [Best region for profit]",
        "",
        f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
    ]
    with open("outputs/insights_summary.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n [save] Insights → outputs/insights_summary.txt")

if __name__ == "__main__":
    df = load()
    summary_stats(df)
    category_analysis(df)
    discount_damage(df)
    top_and_bottom(df)
    regional_view(df)
    save_insights(df)
   
