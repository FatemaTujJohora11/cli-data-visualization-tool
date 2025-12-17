import pandas as pd

def csv_to_json(csv_file="data.csv", json_file="data.json"):
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient="records", indent=4)
    print(f"✅ '{json_file}' created successfully!")

if __name__ == "__main__":
    csv_to_json()