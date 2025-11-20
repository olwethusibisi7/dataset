import os
import pandas as pd


def load_data_from_csv(path: str = "data/recruitment_data.csv") -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sample data not found at {path}")
    df = pd.read_csv(path, parse_dates=["applied_date"])
    return df


def main():
    df = load_data_from_csv()
    print(df.head())


if __name__ == "__main__":
    main()
import os
import sqlite3
import pandas as pd
from pathlib import Path

SAMPLE_CSV = Path(__file__).with_name("recruitment_data_sample.csv")
DB_PATH = Path(__file__).with_name("recruitment.db")


def load_csv(path: Path | str) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path, parse_dates=["application_date", "interview_date"], keep_default_na=False)
    return df


def ensure_db_and_load(csv_path: str | None = None, db_path: str | None = None):
    csv_path = Path(csv_path) if csv_path else SAMPLE_CSV
    db_path = Path(db_path) if db_path else DB_PATH

    if not csv_path.exists():
        print(f"CSV not found at {csv_path}. Using bundled sample: {SAMPLE_CSV}")
        csv_path = SAMPLE_CSV

    print(f"Loading CSV from: {csv_path}")
    df = load_csv(csv_path)
    print(df.head())

    print(f"Writing to SQLite DB at: {db_path}")
    conn = sqlite3.connect(db_path)
    df.to_sql("applications", conn, if_exists="replace", index=False)
    conn.close()
    print("Done. DB populated with `applications` table.")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Load recruitment CSV into local SQLite DB (recruitment.db)")
    parser.add_argument("--csv", help="Path to recruitment CSV (defaults to bundled sample)", default=None)
    parser.add_argument("--db", help="Path to sqlite db (defaults to recruitment.db)", default=None)
    args = parser.parse_args()

    ensure_db_and_load(args.csv, args.db)
