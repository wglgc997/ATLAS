import argparse
import pandas as pd

from pathlib import Path

from src.config.constant import CSV_FIELDNAMES


def parse_args():
    parser = argparse.ArgumentParser(description="Clean a link-check CSV file.")
    parser.add_argument("input_csv", help="CSV file to clean.")
    parser.add_argument(
        "--output",
        help="Output CSV path. Default: <input name>_clean.csv",
    )
    return parser.parse_args()


def output_path(input_csv, output):
    if output:
        return output

    path = Path(input_csv)
    return str(path.with_name(f"{path.stem}_clean{path.suffix}"))


def normalize_schema(df):
    for column in CSV_FIELDNAMES:
        if column not in df.columns:
            df[column] = ""

    return df[CSV_FIELDNAMES]


def clean_dataset(input_csv, output_csv):
    df = pd.read_csv(
        input_csv,
        dtype={
            "OK": "boolean",
            "Redirected": "boolean",
            "HTTPS": "boolean",
            "Internal": "boolean",
            "Source Page": "string",
            "Absolute URL": "string",
            "Region": "string",
            "Status Category": "string",
        },
        low_memory=False,
    )

    df = normalize_schema(df)

    print("First lines: ")
    print(df.head())

    print("\nGeneral information: ")
    print(df.info())

    print("\nDescriptive stats: ")
    print(df.describe(include="all"))

    print("\nNull values by column: ")
    print(df.isnull().sum())

    df = df.dropna(how="all", axis=0)
    df = df.dropna(subset=["Absolute URL"])
    df = df.drop_duplicates(subset=["Absolute URL"])

    duplicate_mask = df.duplicated(subset=["Absolute URL"], keep=False)
    print(df[duplicate_mask].head(20))

    bool_cols = ["OK", "Redirected", "HTTPS", "Internal"]
    for column in bool_cols:
        df[column] = df[column].fillna(False).astype(int)

    df["Region"] = df["Region"].astype(str).str.lower().str.strip()
    df["Status Category"] = df["Status Category"].fillna("unknown")
    df["Response_time"] = df["Response_time"].fillna(0)

    df = normalize_schema(df)
    df = df.reset_index(drop=True)

    print("\nVerification: ")
    print(df.info())
    print(df.isnull().sum())
    print(f"\nTotal lines in the clean dataset: {len(df)}")

    df.to_csv(output_csv, index=False)
    print(f"\nDataset created: {output_csv}")


def main():
    args = parse_args()
    clean_dataset(args.input_csv, output_path(args.input_csv, args.output))


if __name__ == "__main__":
    main()
