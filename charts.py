import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

CLEANED_PATH = "cleaned_data.csv"  # Root folder (from Script 01)
CHARTS_DIR   = "outputs/charts"

# Create charts folder
os.makedirs(CHARTS_DIR, exist_ok=True)

# Consistent professional style
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white", 
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "sans-serif",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
})

def save(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✅ [chart] Saved → {path}")

def load():
    return pd.read_csv(CLEANED_PATH, parse_dates=["order_date", "ship_date"])

def chart_monthly_trend(df):
    monthly = df.groupby("year_month")[["sales", "profit"]].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly["year_month"], monthly["sales"],  label="Revenue", color="#2563EB", linewidth=2)
    ax.plot(monthly["year_month"], monthly["profit"], label="Profit",  color="#16A34A", linewidth=2)
    ax.set_title("📈 Monthly Revenue vs Profit Trend")
    ax.set_xlabel("")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ticks = list(range(0, len(monthly), 6))
    ax.set_xticks(ticks)
    ax.set_xticklabels(monthly["year_month"].iloc[ticks], rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save("01_monthly_trend.png")

def chart_category_bars(df):
    cat = df.groupby("category")[["sales", "profit"]].sum().reset_index()
    x = range(len(cat))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([i - width/2 for i in x], cat["sales"],  width, label="Revenue", color="#2563EB", alpha=0.85)
    ax.bar([i + width/2 for i in x], cat["profit"], width, label="Profit",  color="#16A34A", alpha=0.85)
    ax.set_xticks(list(x))
    ax.set_xticklabels(cat["category"])
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax.set_title("🏆 Revenue vs Profit by Category")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save("02_category_comparison.png")

def chart_discount_scatter(df):
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(sample["discount"], sample["profit_margin_pct"],
                        alpha=0.4, s=20, color="#7C3AED")
    ax.axhline(0, color="#EF4444", linewidth=2, linestyle="--", label="Break-even")
    ax.set_xlabel("Discount %")
    ax.set_ylabel("Profit Margin %")
    ax.set_title("💸 Discount vs Profit Margin\n(each dot = 1 order)")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.legend()
    ax.grid(alpha=0.2)
    save("03_discount_impact.png")

def chart_subcategory_profit(df):
    sub = df.groupby("sub-category")["profit"].sum().sort_values()
    colors = ["#EF4444" if v < 0 else "#10B981" for v in sub.values]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(sub)), sub.values, color=colors)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub.index)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax.set_title("📊 Sub-Category Profit (Red = Loss Making)")
    ax.grid(axis="x", alpha=0.3)
    save("04_subcategory_profit.png")

def chart_correlation_heatmap(df):
    cols = ["sales", "quantity", "discount", "profit", "profit_margin_pct", "shipping_days"]
    corr = df[cols].corr().round(2)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn_r",
                center=0, ax=ax, linewidths=0.5, cbar_kws={"shrink": 0.8})
    ax.set_title("🔗 Correlation Heatmap - Key Metrics")
    save("05_correlation_heatmap.png")

def chart_shipping_mode(df):
    ship = df.groupby("ship_mode")["shipping_days"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(ship.index, ship.values, color="#0EA5E9")
    ax.bar_label(bars, fmt="%.1f days", padding=5, fontsize=11)
    ax.set_xlabel("Shipping Days")
    ax.set_title("🚚 Average Shipping Time by Mode")
    ax.grid(axis="x", alpha=0.3)
    save("06_shipping_analysis.png")

if __name__ == "__main__":
    df = load()
    print("🎨 [charts] Generating professional EDA charts...")
    print("📁 Output folder: outputs/charts/")
    
    chart_monthly_trend(df)
    chart_category_bars(df)
    chart_discount_scatter(df)
    chart_subcategory_profit(df)
    chart_correlation_heatmap(df)
    chart_shipping_mode(df)
    
    print("\n🎉 [done] All 6 charts saved to outputs/charts/")
    print("📄 Perfect for your hackathon report & presentation!")
    print("💡 Key finding: Use 03_discount_impact.png as your headline chart!")