import pandas as pd
import sqlite3
import os

CLEANED_PATH = "cleaned_data.csv"
OUTPUT_DIR   = "outputs"

def get_connection():
    df = pd.read_csv(CLEANED_PATH, parse_dates=["order_date", "ship_date"])
    con = sqlite3.connect(":memory:")
    df.to_sql("orders", con, index=False, if_exists="replace")
    print(" [sql] 9994 rows loaded into SQLite database")
    return con

def run_and_save(con, query, filename, label):
    result = pd.read_sql_query(query, con)
    print(f"\n── {label} ──")
    print(result.to_string(index=False))
    path = os.path.join(OUTPUT_DIR, filename)
    result.to_csv(path, index=False)
    print(f"    saved → {path}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    con = get_connection()

    # Query 1: Monthly trend
    run_and_save(con, """
        SELECT year_month,
               ROUND(SUM(sales), 0)  AS revenue,
               ROUND(SUM(profit), 0) AS profit
        FROM   orders
        GROUP  BY year_month
        ORDER  BY year_month
    """, "01_monthly_trend.csv", "Monthly revenue trend")

    # Query 2: Top 10 products
    run_and_save(con, """
        SELECT "product_name",
               ROUND(SUM(sales), 0)  AS total_revenue,
               ROUND(SUM(profit), 0) AS total_profit
        FROM   orders
        GROUP BY "product_name"
        ORDER BY total_revenue DESC
        LIMIT 10
    """, "02_top10_products.csv", "Top 10 products")

    # Query 3: Category margins
    run_and_save(con, """
        SELECT "category",
               ROUND(SUM(sales), 0)                        AS revenue,
               ROUND(SUM(profit), 0)                       AS profit,
               ROUND(SUM(profit)/SUM(sales)*100, 1)        AS margin_pct
        FROM   orders
        GROUP  BY "category"
        ORDER  BY margin_pct DESC
    """, "03_category_margins.csv", "Category profit margins")

    # FIXED Query 4: Discount impact
    run_and_save(con, """
        WITH discount_buckets AS (
            SELECT *,
                   CASE 
                       WHEN discount < 0 THEN '0%'
                       WHEN discount < 0.1 THEN '1-10%'
                       WHEN discount < 0.2 THEN '11-20%'
                       WHEN discount < 0.3 THEN '21-30%'
                       WHEN discount < 0.5 THEN '31-50%'
                       ELSE '50%+'
                   END AS discount_bucket
            FROM orders
        )
        SELECT discount_bucket,
               COUNT(*)                    AS orders,
               ROUND(AVG(profit_margin_pct), 2) AS avg_margin_pct,
               ROUND(SUM(profit), 0)       AS total_profit
        FROM discount_buckets
        GROUP BY discount_bucket
        ORDER BY discount_bucket
    """, "04_discount_impact.csv", "Discount vs Margin")

    # Query 5: Top customers
    run_and_save(con, """
        SELECT "customer_name",
               COUNT(DISTINCT "order_id") AS orders,
               ROUND(SUM(sales), 0)     AS lifetime_value
        FROM   orders
        GROUP BY "customer_name"
        ORDER BY lifetime_value DESC
        LIMIT 10
    """, "05_top_customers.csv", "Top 10 customers")

    # Query 6: Shipping
    run_and_save(con, """
        SELECT "ship_mode",
               ROUND(AVG(shipping_days), 1) AS avg_days,
               COUNT(*)                     AS orders
        FROM   orders
        GROUP BY "ship_mode"
        ORDER BY avg_days ASC
    """, "06_shipping_analysis.csv", "Shipping performance")

    # Query 7: YoY growth
    run_and_save(con, """
        SELECT year,
               ROUND(SUM(sales), 0)  AS revenue,
               ROUND(SUM(profit), 0) AS profit
        FROM   orders
        GROUP  BY year
        ORDER  BY year
    """, "07_yoy_growth.csv", "Year-over-year growth")

    # FIXED Query 8: Loss sub-categories
    run_and_save(con, """
        SELECT "sub-category",
               ROUND(SUM(profit), 0) AS total_profit,
               COUNT(*)              AS orders
        FROM   orders
        GROUP BY "sub-category"
        HAVING SUM(profit) < 0
        ORDER BY total_profit ASC
    """, "08_loss_subcategories.csv", "Loss-making sub-categories")

    con.close()
    print(" All 8 CSVs saved to outputs/")
