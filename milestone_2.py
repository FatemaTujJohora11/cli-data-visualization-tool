from pathlib import Path
import pandas as pd

# --- Load CSV or JSON file ---
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

# --- Show data ---
def show_data(df, n=5):
    print(df.head(n))
    print(f"\nTotal rows: {len(df)}")

# --- Main program ---
def main():
    file_name = input("Enter file name (data.csv or data.json): ").strip()
    df = load_data(file_name)
    if df is None:
        return

    # keep a backup copy
    original_df = df.copy()

    print("✅ Data loaded! Type 'help' to see all commands.")

    while True:
        cmd = input(">> ").strip().lower()

        if cmd == "help":
            print("""
Commands:
  help      Show this help message
  show [n]  Show first n rows (default 5)
  cols      List column names
  dtypes    Show column data types
  reset     Reset to original data
  exit      Quit the program
""")

        elif cmd.startswith("show"):
            parts = cmd.split()
            n = int(parts[1]) if len(parts) > 1 else 5
            show_data(df, n)

        elif cmd == "cols":
            print(", ".join(df.columns))

        elif cmd == "dtypes":
            print(df.dtypes)

        elif cmd == "reset":
            df = original_df.copy()
            print("🔄 Data reset to original file.")

        elif cmd == "exit":
            print("👋 Goodbye!")
            break

        else:
            print("Unknown command. Type 'help' for options.")

if __name__ == "__main__":
    main()
