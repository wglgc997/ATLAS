import csv
import os

from src.config.constant import CSV_FIELDNAMES


def save_csv(path, rows):
    """Create and structure the CSV file"""
    ensure_csv_schema(path)

    file_exist = (
        os.path.isfile(path) and os.path.getsize(path) > 0
    )  # Verify if csv file already exist

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")

        if not file_exist:  # Write just one time
            writer.writeheader()

        writer.writerows(rows)  # Save the data


def ensure_csv_schema(path):
    """Keep existing and new CSV files on the same header schema."""
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_fieldnames = reader.fieldnames

        if existing_fieldnames == CSV_FIELDNAMES:
            return
        tmp_path = f"{path}.tmp"

        with open(tmp_path, "w", newline="", encoding="utf-8") as tmp_file:
            writer = csv.DictWriter(
                tmp_file, fieldnames=CSV_FIELDNAMES, extrasaction="ignore"
            )
            writer.writeheader()

            for row in reader:
                writer.writerow({field: row.get(field, "") for field in CSV_FIELDNAMES})

    os.replace(tmp_path, path)
