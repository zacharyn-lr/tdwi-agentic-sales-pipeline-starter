import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def load_and_clean_data():
    df = pd.read_csv("data/messy_sales_data.csv")

    # Exact duplicate order rows are present in the source file.
    df = df.drop_duplicates()

    # Dates mix ISO (2025-01-15) and US (01/19/2025) formats.
    df["date"] = pd.to_datetime(df["date"], format="mixed")

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Source revenue includes "-" placeholders and values that do not match
    # price * quantity. Recalculate so metrics use a consistent numeric column.
    df["revenue"] = df["price"] * df["quantity"]

    return df


def generate_metrics(df):
    total_revenue = df["revenue"].sum()
    top_customers = df.groupby("customer_id")["revenue"].sum().nlargest(5)
    avg_order_value = df["revenue"].mean()
    return total_revenue, top_customers, avg_order_value


def create_chart(df):
    daily_revenue = df.groupby("date")["revenue"].sum().sort_index()
    # Bar plots reject a DatetimeIndex in pandas 3; use date strings as labels.
    daily_revenue.index = daily_revenue.index.strftime("%Y-%m-%d")

    plt.figure(figsize=(10, 6))
    daily_revenue.plot(kind="bar")
    plt.title("Daily Revenue Trend")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig("report.png")
    plt.close()


def mock_encrypt_export(df, secret_key):
    # Uses the secret (REPORT_EXPORT_KEY)
    os.makedirs("output", exist_ok=True)
    encrypted_file = "output/encrypted_sales_report.csv"
    df.to_csv(encrypted_file, index=False)
    if secret_key:
        print(f"Exported encrypted report using secret: {secret_key[:4]}...")
    else:
        print("Exported sales report CSV (REPORT_EXPORT_KEY is not set).")


def main():
    df = load_and_clean_data()
    total, top, avg = generate_metrics(df)
    create_chart(df)

    secret_key = os.getenv("REPORT_EXPORT_KEY")
    mock_encrypt_export(df, secret_key)

    print("Report generated!")
    print(f"Total Revenue: ${total:,.2f}")
    print(f"Avg Order Value: ${avg:,.2f}")
    print(f"Top Customers:\n{top}")


if __name__ == "__main__":
    main()
