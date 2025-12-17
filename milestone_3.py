from pathlib import Path
import pandas as pd

# ----------------- Basic loading & utilities -----------------
def load_data(file_name):
    path = Path(file_name)
    if not path.exists():
        print("❌ File not found:", file_name)
        return None
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext == ".json":
        # try normal JSON, then JSON lines
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)
    else:
        print("⚠️ Only .csv or .json files are supported.")
        return None

def show_data(df, n=5):
    print(df.head(n))
    print(f"\nTotal rows: {len(df)}")

def column_map(df):
    """case-insensitive map: 'age' -> 'Age' (real name)"""
    return {c.lower(): c for c in df.columns}

# ------------- Filter parsing (simple & safe) ----------------
OPS = ("==", "!=", ">=", "<=", ">", "<", "~")  # ~ means contains (case-insensitive)

def coerce_value(text):
    """turn token into int/float/bool/None/str"""
    t = text.strip()
    # quoted string
    if len(t) >= 2 and t[0] == t[-1] and t[0] in ("'", '"'):
        return t[1:-1]
    low = t.lower()
    if low in ("none", "null"): return None
    if low in ("true", "false"): return low == "true"
    # try number
    try:
        return float(t) if "." in t else int(t)
    except ValueError:
        return t

def parse_condition(token):
    token = token.strip()
    for op in ("==", "!=", ">=", "<=", ">", "<", "~"):
        if op in token:
            left, right = token.split(op, 1)
            left, right = left.strip(), right.strip()
            if not left:
                raise ValueError("Missing column name in condition.")
            if op != "~" and right == "":
                raise ValueError("Missing value in condition.")
            return left, op, coerce_value(right)
    raise ValueError(f"Invalid condition: {token!r}. Use one of {OPS}.")

def apply_condition(df, col, op, value):
    s = df[col]
    if op == "~":  # substring contains, case-insensitive
        return s.astype(str).str.contains(str(value), case=False, na=False)

    left = s
    right = value
    # try numeric compare when possible
    if not pd.api.types.is_numeric_dtype(left):
        left = pd.to_numeric(left, errors="coerce")
    if isinstance(right, str) and pd.api.types.is_numeric_dtype(left):
        try:
            right = float(right) if "." in right else int(right)
        except ValueError:
            # comparing numeric column to non-numeric text: always False
            return pd.Series([False] * len(df), index=df.index)

    if op == "==": return left == right
    if op == "!=": return left != right
    if op == ">":  return left > right
    if op == ">=": return left >= right
    if op == "<":  return left < right
    if op == "<=": return left <= right
    raise ValueError(f"Unsupported operator: {op}")

def run_filter(df, expr):
    """
    Syntax:
      filter Age>25
      filter Department==IT
      filter Age>=28,Department==IT
      filter Name~ali
    Comma means AND.
    """
    if not expr.strip():
        raise ValueError("Filter expression is empty.")
    cmap = column_map(df)
    tokens = [t for t in (x.strip() for x in expr.split(",")) if t]
    mask = pd.Series([True] * len(df), index=df.index)
    for t in tokens:
        col_raw, op, val = parse_condition(t)
        key = col_raw.lower()
        if key not in cmap:
            raise KeyError(f"Unknown column '{col_raw}'. Available: {', '.join(df.columns)}")
        col = cmap[key]
        mask &= apply_condition(df, col, op, val)
    return df[mask]

# --------------------- Sorting (easy) ------------------------
def run_sort(df, expr):
    """
    Syntax:
      sort Salary,desc
      sort Name
    """
    if not expr.strip():
        raise ValueError("Sort expression is empty.")
    parts = [p.strip() for p in expr.split(",") if p.strip()]
    col_raw = parts[0]
    order = parts[1].lower() if len(parts) > 1 else "asc"
    if order not in ("asc", "desc"):
        raise ValueError("Order must be 'asc' or 'desc'.")
    cmap = column_map(df)
    key = col_raw.lower()
    if key not in cmap:
        raise KeyError(f"Unknown column '{col_raw}'. Available: {', '.join(df.columns)}")
    col = cmap[key]
    return df.sort_values(by=[col], ascending=(order == "asc"), kind="mergesort")

# --------------------- Interactive REPL ---------------------
HELP = """
Commands:
  help                      Show this help
  show [n]                  Show first n rows (default 5)
  cols                      List column names
  dtypes                    Show column data types
  filter <cond>[,<cond>...] AND conditions (== != > >= < <= ~)
                            e.g., filter Age>25
                                  filter Department==IT
                                  filter Age>=28,Department==IT
                                  filter Name~ali
  sort <col>[,asc|desc]     e.g., sort Salary,desc
  reset                     Reset to original data
  exit                      Quit
"""

def main():
    file_name = input("Enter file name (data.csv or data.json): ").strip()
    df = load_data(file_name)
    if df is None:
        return
    original = df.copy()
    current = df.copy()

    print("✅ Data loaded! Type 'help' for commands.")

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        if not line:
            continue

        # split command and arg
        if " " in line:
            cmd, arg = line.split(" ", 1)
            arg = arg.strip()
        else:
            cmd, arg = line, ""

        cmd_low = cmd.lower()

        try:
            if cmd_low == "help":
                print(HELP)
            elif cmd_low == "show":
                n = int(arg) if arg else 5
                show_data(current, n)
            elif cmd_low == "cols":
                print(", ".join(current.columns))
            elif cmd_low == "dtypes":
                print(current.dtypes)
            elif cmd_low == "filter":
                if not arg:
                    print("Usage: filter <cond>[,<cond>...]")
                    continue
                current = run_filter(current, arg)
                print(f"Filtered rows: {len(current)}")
            elif cmd_low == "sort":
                if not arg:
                    print("Usage: sort <col>[,asc|desc]")
                    continue
                current = run_sort(current, arg)
                print("Sorted.")
            elif cmd_low == "reset":
                current = original.copy()
                print("🔄 Data reset to original file.")
            elif cmd_low in ("exit", "quit"):
                print("👋 Goodbye!")
                break
            else:
                print("Unknown command. Type 'help' for options.")
        except Exception as e:
            print(f"⚠️ {e}")

if __name__ == "__main__":
    main()
