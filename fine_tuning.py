

import argparse
import pandas as pd
import json
from tqdm import tqdm
import os

def row_to_symptom_text(row: pd.Series) -> str:
    # Collect columns where value==1 (assuming one-hot)
    parts = []
    for col, val in row.items():
        if col.lower().startswith("disease") or col.lower().startswith("label"):
            continue
        # assume numeric 1/0 or True/False
        try:
            if float(val) == 1.0:
                parts.append(col)
        except Exception:
            # if text, skip
            pass
    return ", ".join(parts) if parts else row.to_json()

def main(input_csv: str, disease_file: str, out: str):
    df = pd.read_csv(input_csv)
    disease_df = pd.read_csv(disease_file) if disease_file and os.path.exists(disease_file) else None

    examples = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        symptom_text = row_to_symptom_text(row)
        # use disease label column heuristics
        disease_label = None
        for c in df.columns:
            if "disease" in c.lower() or "label" in c.lower():
                disease_label = str(row[c])
                break
        disease_description = ""
        if disease_df is not None and 'disease' in disease_df.columns:
            # try match
            match = disease_df[disease_df['disease'].str.lower() == str(disease_label).lower()]
            if not match.empty:
                disease_description = match.iloc[0].get('answer', '')
        # build assistant response
        assistant = f"Probable condition: {disease_label}\nDescription: {disease_description}\nRecommended next steps: Further tests and referral to clinician."
        examples.append({"prompt": f"Patient reports: {symptom_text}\n", "completion": " " + assistant})

    # Write JSONL
    with open(out, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(examples)} examples to {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="CSV with symptom one-hot columns")
    parser.add_argument("--disease_file", required=False, help="CSV mapping disease->description")
    parser.add_argument("--out", required=True, help="Output JSONL file")
    args = parser.parse_args()
    main(args.input_csv, args.disease_file, args.out)

