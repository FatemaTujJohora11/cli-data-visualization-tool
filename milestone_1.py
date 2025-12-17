# --- Step 1: import required modules ---
from pathlib import Path
import pandas as pd

# --- Step 2: function to load CSV or JSON file ---
def load_data(file_name):
    path = Path(file_name)

    if not path.exists():
        print("❌ File not found:", file_name)
        return None

    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".json":
        df = pd.read_json(path)
    else:
        print("⚠️ Only .csv or .json files are supported.")
        return None

    return df

# --- Step 3: function to show top rows of data ---
def show_data(df, n=5):
    print(df.head(n))
    print(f"\nTotal rows: {len(df)}")

# --- Step 4: interactive menu ---
def main():
    file_name = input("Enter file name (data.csv or data.json): ")
    df = load_data(file_name)
    if df is None:
        return

    print("✅ Data loaded! Type 'show' or 'show 5', 'exit' to quit.")

    while True:
        cmd = input(">> ").strip().lower()
        if cmd.startswith("show"):
            parts = cmd.split()
            n = int(parts[1]) if len(parts) > 1 else 5
            show_data(df, n)
        elif cmd == "exit":
            print("👋 Goodbye!")
            break
        else:
            print("Unknown command. Use 'show' or 'exit'.")

# --- Step 5: run main ---
if __name__ == "__main__":
    main()
