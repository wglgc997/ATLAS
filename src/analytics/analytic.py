import argparse
import pandas as pd
import matplotlib.pyplot as plt
import pylab as pl


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze a link-check CSV file.")
    parser.add_argument("csv_path", help="CSV file to analyze.")
    return parser.parse_args()


def require_columns(df, columns, report_name):
    missing = [column for column in columns if column not in df.columns]

    if missing:
        print(f"\n===== {report_name} SKIPPED =====\n")
        print(f"Missing column(s): {', '.join(missing)}")
        print(f"Available columns: {', '.join(df.columns)}")
        return False

    return True


def diagnose(df):
    """X-ray of the dataset."""
    if not require_columns(df, ["Absolute URL"], "DATASET DIAGNOSE"):
        return

    print("=" * 60)
    print(" DATASET DIAGNOSE")
    print("=" * 60)

    print(f"\nDimension: {df.shape[0]:,} lines x {df.shape[1]} columns")

    print("\nMemory use:")
    mem_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    print(f" {mem_mb:.2f} MB")

    print("\nNull values by column:")
    nulls = df.isnull().sum()
    nulls_pct = (df.isnull().sum() / len(df) * 100).round(2)
    resume_nulls = pd.DataFrame({"Nulls": nulls, "Percentual (%)": nulls_pct})
    print(resume_nulls[resume_nulls["Nulls"] > 0].to_string())
    if nulls.sum() == 0:
        print("No null values found")

    print("\nDuplicates in 'Absolute URL':")
    dupes = df.duplicated(subset=["Absolute URL"]).sum()
    print(f" {dupes:,} duplicates")

    print("\nData types:")
    print(df.dtypes.to_string())


def broken_by_region(df):
    if not require_columns(df, ["Region", "OK", "Error"], "BROKEN LINKS BY REGION"):
        return

    broken = df[(df["OK"].ne(True)) | (df["Error"].notna())]

    result = broken.groupby("Region").size().sort_values(ascending=False)

    print("\n===== BROKEN LINKS BY REGION =====\n")
    print(result)


def response_time_by_region(df):
    if not require_columns(
        df, ["Region", "Response_time"], "AVERAGE RESPONSE TIME BY REGION"
    ):
        return

    result = (
        df.groupby("Region")["Response_time"]
        .mean()
        .sort_values(ascending=False)
        .round(2)
    )

    print("\n===== AVERAGE RESPONSE TIME BY REGION =====\n")
    print(result)


def problematic_pages(df):
    if not require_columns(
        df, ["Source Page", "OK", "Error"], "PAGES WITH MOST BROKEN LINKS"
    ):
        return

    broken = df[(df["OK"].ne(True)) | (df["Error"].notna())]

    result = broken.groupby("Source Page").size().sort_values(ascending=False).head(20)

    print("\n===== PAGES WITH MOST BROKEN LINKS =====\n")
    print(result)


def slowest_pages(df):
    if not require_columns(
        df, ["Source Page", "Response_time"], "SLOWEST SOURCE PAGES"
    ):
        return

    result = (
        df.groupby("Source Page")["Response_time"]
        .mean()
        .sort_values(ascending=False)
        .head(20)
        .round(2)
    )

    print("\n===== SLOWEST SOURCE PAGES =====\n")
    print(result)


def status_category_distribution(df):

    result = df["Status Category"].value_counts()

    print("\n===== STATUS CATEGORY DISTRIBUTION =====\n")
    print(result)


def top_status_code(df):

    result = df["Status"].value_counts().sort_values(ascending=False)

    print("\n===== TOP STATUS CODES =====\n")
    print(result)


def status_by_region(df):

    result = df.groupby(["Region", "Status Category"]).size().unstack(fill_value=0)

    print("\n===== STATUS BY REGION =====\n")
    print(result)


# MATPLOTLIB
def plot_broken_by_region(df):

    broken = df[(df["OK"].ne(True)) | (df["Error"].notna())]

    result = broken.groupby("Region").size().sort_values(ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    result.plot(kind="bar")
    plt.title("Broken Links by Region")
    plt.xlabel("Region")
    plt.ylabel("Broken Links")
    pl.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_response_time(df):

    result = (
        df.groupby("Region")["Response_time"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 6))
    result.plot(kind="bar")
    plt.title("Average Response Time By Region")
    plt.xlabel("Region")
    plt.ylabel("Seconds")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_status_categories(df):

    result = df["Status Category"].value_counts()

    plt.figure(figsize=(8, 8))
    result.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Status Category Distribution")
    plt.ylabel("")
    plt.show()


def main():
    args = parse_args()

    df = pd.read_csv(args.csv_path)

    diagnose(df)
    broken_by_region(df)
    response_time_by_region(df)
    problematic_pages(df)
    slowest_pages(df)
    status_category_distribution(df)
    top_status_code(df)
    status_by_region(df)
    plot_broken_by_region(df)
    plot_response_time(df)
    plot_status_categories(df)


if __name__ == "__main__":
    main()
