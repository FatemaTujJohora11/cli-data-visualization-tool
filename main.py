from pathlib import Path
import pandas as pd

# ---------- load FUNCTION ----------
# Loads CSV or JSON file based on extension
def load(path):
    p = Path(path)
    if not p.exists():
        print("❌ File not found")
        return None
    try:
        return pd.read_json(p)          # Try JSON
    except:
        try:
            return pd.read_json(p, lines=True)   # Try JSON Lines
        except:
            try:
                return pd.read_csv(p)   # Try CSV
            except:
                print("⚠️ Use .csv or .json")
                return None


# ---------- helper for case-insensitive column match ----------
def cmap(df):
    return {c.lower(): c for c in df.columns}


# ---------- show first N rows ----------
def show(df, n=5):
    print(df.head(n))
    print(f"\nRows in view: {len(df)}")


# ALL supported filter operators
OPS = ("==", "!=", ">=", "<=", ">", "<", "~")


# ---------- convert string to appropriate type ----------
def to_val(s):
    s = s.strip()
    # quoted string
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    low = s.lower()
    if low in ("none", "null"):
        return None
    if low in ("true", "false"):
        return low == "true"
    # try numeric
    try:
        return float(s) if "." in s else int(s)
    except:
        return s


# ---------- parse condition like Age>=30 ----------
def parse_cond(tok):
    for op in OPS:
        if op in tok:
            L, R = tok.split(op, 1)
            L, R = L.strip(), R.strip()
            if not L:
                raise ValueError("Missing column")
            if op != "~" and R == "":
                raise ValueError("Missing value")
            return L, op, to_val(R)
    raise ValueError(f"Bad condition: {tok}")


# ---------- create boolean mask for filtering ----------
def mask_for(df, col, op, val):
    s = df[col]

    # substring search operator ~
    if op == "~":
        return s.astype(str).str.contains(str(val), case=False, na=False)

    # numeric vs string comparison logic
    if isinstance(val, (int, float)):
        left = s if pd.api.types.is_numeric_dtype(s) else pd.to_numeric(s, errors="coerce")
        right = val
    else:
        left = s.astype(str)
        right = str(val)

    ops = {
        "==": left == right,
        "!=": left != right,
        ">":  left > right,
        ">=": left >= right,
        "<":  left < right,
        "<=": left <= right,
    }
    return ops[op]


# ---------- FILTER LOGIC ----------
# Runs all conditions and applies them with AND logic
def run_filter(df, expr):
    tokens = [t.strip() for t in expr.split(",") if t.strip()]
    m = cmap(df)
    mask = pd.Series([True] * len(df), index=df.index)

    for t in tokens:
        col_raw, op, val = parse_cond(t)   # break condition into parts
        key = col_raw.lower()

        if key not in m:
            raise KeyError(f"Unknown column '{col_raw}'. Use: {', '.join(df.columns)}")

        # combine masks
        mask &= mask_for(df, m[key], op, val)

    return df[mask]   # return only matched rows


# ---------- SORT LOGIC ----------
def run_sort(df, expr):
    parts = [p.strip() for p in expr.split(",") if p.strip()]

    if not parts:
        raise ValueError("Usage: sort <col>[,asc|desc]")

    col_raw = parts[0]
    order = parts[1].lower() if len(parts) > 1 else "asc"

    if order not in ("asc", "desc"):
        raise ValueError("Order must be asc/desc")

    m = cmap(df)
    key = col_raw.lower()

    if key not in m:
        raise KeyError(f"Unknown column '{col_raw}'. Use: {', '.join(df.columns)}")

    # mergesort guarantees stability
    return df.sort_values(by=[m[key]], ascending=(order == "asc"), kind="mergesort")


# ---------- PAGINATION ----------
class Pager:
    def __init__(self, df, size=5):
        self.set_df(df)
        self.size = max(1, int(size))
        self.i = 1  # current page number

    # reset page when data changes (filter/sort/reset)
    def set_df(self, df):
        self.df = df
        self.i = 1

    # calculate total pages
    @property
    def pages(self):
        return max(1, (len(self.df) - 1) // self.size + 1)

    # return only the rows of the current page
    def view(self):
        a = (self.i - 1) * self.size
        b = a + self.size
        return self.df.iloc[a:b]


# ---------- Help Command ----------
HELP = """Commands:
  help                      Show help
  show [N]                  Show current page (or top N rows)
  cols                      List columns
  dtypes                    Show data types
  filter <cond>[,<cond>...] Apply filters (AND)
  sort <col>[,asc|desc]     Sort rows
  pagesize N                Set rows per page
  page N                    Jump to page
  next                      Next page
  prev                      Previous page
  export <file>             Export all visible rows (filtered/sorted)
  export_page <file>        Export only current page
  reset                     Reset data + pagesize + page
  exit                      Quit program
"""


# ---------- MAIN LOOP ----------
def main():
    # 1. Load file
    path = input("Enter file name (data.csv or data.json): ").strip()
    df = load(path)
    if df is None:
        return

    original = df.copy()     # keep original data for reset
    current = df.copy()      # working dataset
    pager = Pager(current, 5)

    print("✅ Loaded. Type 'help'.")

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Bye")
            break

        if not line:
            continue

        cmd, arg = (line.split(" ", 1) + [""])[:2]
        cmd = cmd.lower().strip()
        arg = arg.strip()

        try:
            # ------- show help -------
            if cmd == "help":
                print(HELP)

            # ------- show data -------
            elif cmd == "show":
                if arg:
                    show(current, int(arg))
                else:
                    page = pager.view()
                    print(page)
                    print(f"\nPage {pager.i}/{pager.pages} | Rows: {len(current)}")

            # ------- show columns -------
            elif cmd == "cols":
                print(", ".join(current.columns))

            # ------- show data types -------
            elif cmd == "dtypes":
                print(current.dtypes)

            # ------- FILTER FEATURE -------
            elif cmd == "filter":
                if not arg:
                    print("Usage: filter <cond>[,<cond>...]")
                    continue
                current = run_filter(current, arg)
                pager.set_df(current)
                print(f"Filtered rows: {len(current)} (Page {pager.i}/{pager.pages})")

            # ------- SORT FEATURE -------
            elif cmd == "sort":
                if not arg:
                    print("Usage: sort <col>[,asc|desc]")
                    continue
                current = run_sort(current, arg)
                pager.set_df(current)
                print("Sorted.")

            # ------- SET PAGE SIZE -------
            elif cmd == "pagesize":
                if not arg.isdigit():
                    print("Usage: pagesize N")
                    continue
                pager.size = max(1, int(arg))
                pager.i = 1
                print(f"Page size: {pager.size}")

            # ------- JUMP TO PAGE -------
            elif cmd == "page":
                if not arg.isdigit():
                    print("Usage: page N")
                    continue
                pager.i = max(1, min(int(arg), pager.pages))
                print(f"Page {pager.i}/{pager.pages}")

            # ------- NEXT PAGE -------
            elif cmd == "next":
                if pager.i >= pager.pages:
                    print("No more pages.")
                else:
                    pager.i += 1
                print(f"Page {pager.i}/{pager.pages}")

            # ------- PREVIOUS PAGE -------
            elif cmd == "prev":
                if pager.i <= 1:
                    print("Already at first page.")
                else:
                    pager.i -= 1
                print(f"Page {pager.i}/{pager.pages}")

            # ------- EXPORT FILTERED/SORTED DATA -------
            elif cmd == "export":
                if not arg:
                    print("Usage: export <file>")
                    continue
                out = Path(arg)

                df_to_save = current.copy()   # only visible rows

                if out.suffix.lower() == ".json":
                    df_to_save.to_json(out, orient="records", indent=2)
                else:
                    df_to_save.to_csv(out, index=False)

                print(f"💾 Saved visible rows: {out}")

            # ------- EXPORT PAGE ONLY -------
            elif cmd == "export_page":
                if not arg:
                    print("Usage: export_page <file>")
                    continue
                out = Path(arg)

                page_df = pager.view().copy()   # only current page

                if out.suffix.lower() == ".json":
                    page_df.to_json(out, orient="records", indent=2)
                else:
                    page_df.to_csv(out, index=False)

                print(f"💾 Saved current page: {out}")

            # ------- RESET FEATURE -------
            elif cmd == "reset":
                current = original.copy()
                pager.set_df(current)
                pager.size = 5      # reset page size
                pager.i = 1         # reset to page 1
                print("🔄 Reset to original data and default pagesize (5).")

            # ------- EXIT -------
            elif cmd in ("exit", "quit"):
                print("👋 Bye")
                break

            else:
                print("Unknown command. Type 'help'.")

        except Exception as e:
            print(f"⚠️ {e}")


if __name__ == "__main__":
    main()
