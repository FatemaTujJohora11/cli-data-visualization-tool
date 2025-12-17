# CLI Data Visualization Tool

## 1. Brief Description

This program is a Command-Line Interface (CLI) tool that allows users to load, view, filter, sort, paginate, and export data from CSV or JSON files. It is designed to make data exploration easy from the terminal without needing GUI applications such as Excel. The tool supports case-insensitive column matching, multiple filter operators, stable sorting, and page-based viewing for large datasets.

---

## 2. How to Run the Program

### Requirements
- Python 3.x
- pandas library  
  Install using:
pip install pandas

### Running the Program
1. Open a terminal or PowerShell window.
2. Navigate to the folder containing the Python file.
3. Run:
python milestone_4.py
4. When prompted, enter a CSV or JSON filename:
Enter file name (data.csv or data.json):

5. Type `help` to see all supported commands.

---

## 3. Features

### 🔹 File Loading
- Supports `.csv`, `.json`, and JSON Lines.
- Automatic file-type detection.
- Error handling for missing or invalid files.

### 🔹 Data Viewing
- `show` → View current page
- `show N` → View first N rows
- `cols` → List all columns
- `dtypes` → Show data types

### 🔹 Filtering
Supports multiple conditions separated by commas:
filter Age>=30

Available operators:  
`==`, `!=`, `>=`, `<=`, `>`, `<`, `~` (contains search)

### 🔹 Sorting

sort Age,desc
Uses stable mergesort.

### 🔹 Pagination
pagesize N
next
prev
page N
Automatically updates after filtering or sorting.

### 🔹 Exporting
export output.csv
export output.json
export_page page1.csv
Allows saving all visible rows or only the current page.

### 🔹 Reset System
Restores:
- Original data  
- Page size = 5  
- Page number = 1  

---

## 4. Known Bugs or Limitations

- The filter system does not support logical `AND/OR` expressions beyond comma-separated AND.
- Very large datasets may load slowly due to pandas performance constraints.
- Complex nested filtering expressions (e.g., parentheses) are not supported.
- No graphical interface; all interaction is through the CLI.

---

## End of README
