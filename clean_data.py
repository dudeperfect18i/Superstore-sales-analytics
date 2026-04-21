import pandas as pd
import numpy as np
import os

# ── paths ─────────────────────────────────────────────────────────────────────
RAW_PATH     = "superstore.csv"     
CLEANED_PATH = "cleaned_data.csv"       

def load_data(path):
    """Load raw CSV. Try UTF-8 first, fall back to latin-1."""
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")
    print(f"[load]  {df.shape[0]} rows, {df.shape[1]} columns loaded")
    return df

def inspect(df):
    print("\n── Column types ──")
    print(df.dtypes)
    print("\n── Missing values ──")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    print("\n── Duplicate rows ──")
    print(df.duplicated().sum())

def clean(df):
 
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    before = len(df)
    df = df.drop_duplicates()
    print(f"[clean] Removed {before - len(df)} duplicate rows")


    df["order_date"] = pd.to_datetime(df["order_date"], dayfirst=False)
    df["ship_date"]  = pd.to_datetime(df["ship_date"],  dayfirst=False)

  
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].fillna(0).astype(int)

    df = df.dropna(subset=["sales", "profit"])
    print(f"[clean] {len(df)} rows after null removal")


    df["profit_margin_pct"] = (df["profit"] / df["sales"] * 100).round(2)
    df["shipping_days"]     = (df["ship_date"] - df["order_date"]).dt.days
    df["year"]              = df["order_date"].dt.year
    df["month"]             = df["order_date"].dt.month
    df["year_month"]        = df["order_date"].dt.to_period("M").astype(str)
    df["is_loss"]           = df["profit"] < 0

   
    str_cols = ["segment", "category", "sub-category", "region", "ship_mode"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    return df

def save(df, path):
    df.to_csv(path, index=False)
    print(f"[save]  Cleaned data saved → {path}")

if __name__ == "__main__":
    df = load_data(RAW_PATH)
    inspect(df)
    df = clean(df)
    save(df, CLEANED_PATH)
    print("\n[done]  Script 01 complete. Run 02_explore_data.py next.")
