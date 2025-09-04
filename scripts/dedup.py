# scripts/dedup.py
import pandas as pd
from tqdm import tqdm
import sys
import os

def deduplicate_sequences(
    input_file="intermediate_files/3a_cleaned_file_with_sequences.txt",
    output_file="intermediate_files/4a_deduplicated_file_with_sequences.txt",
    filtered_out_file="intermediate_files/4b_deduplicated_removed_entries.txt"
):
    if not os.path.exists(input_file):
        sys.exit(f"❌ File not found: {input_file}")

    df = pd.read_csv(input_file, sep="\t", dtype=str)
    df.columns = [col.lower() for col in df.columns]

    required_columns = ["fetched_sequence", "mutation", "frag_numb"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        sys.exit(f"❌ Missing required columns: {missing_cols}")

    duplicated_mask = df.duplicated(subset="fetched_sequence", keep=False)
    df["duplicated"] = duplicated_mask.map({True: "yes", False: "no"})

    # Move "duplicated" column to second position
    cols = df.columns.tolist()
    cols.insert(1, cols.pop(cols.index("duplicated")))
    df = df[cols]

    total = len(df)
    duplicate_count = duplicated_mask.sum()
    unique_count = total - duplicate_count

    print(f"Total entries: {total}")
    print(f"Unique entries: {unique_count} ({(unique_count / total) * 100:.2f}%)")
    print(f"Duplicated entries: {duplicate_count} ({(duplicate_count / total) * 100:.2f}%)")

    user_input = input("Perform deduplication? (y/n): ").strip().lower()
    if user_input not in {"y", "yes"}:
        print("Skipping deduplication. Using original input file.")
        return  # Exit the function, but don't kill the script


    seen = {}
    filtered_out_rows = []
    deduplicated_rows = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Deduplicating", unit="rows"):
        seq = row["fetched_sequence"]
        mutation = row["mutation"]

        if seq not in seen:
            seen[seq] = row.copy()
            deduplicated_rows.append(seen[seq])
        else:
            prev_row = seen[seq]
            prev_mut = prev_row["mutation"]
            if prev_mut == mutation:
                seen[seq]["mutation"] = f"{mutation}_multi"
            else:
                # Combine different mutations with underscore
                merged = "_".join(sorted(set(prev_mut.split("_") + mutation.split("_"))))
                seen[seq]["mutation"] = merged
            row["kept_frag_numb"] = seen[seq]["frag_numb"]
            filtered_out_rows.append(row)


    deduplicated_df = pd.DataFrame(deduplicated_rows)
    filtered_out_df = pd.DataFrame(filtered_out_rows)

    deduplicated_df.to_csv(output_file, sep="\t", index=False)
    filtered_out_df.to_csv(filtered_out_file, sep="\t", index=False)

    print(f"\nDeduplicated file saved to: {output_file}")
    print(f"Filtered-out duplicates saved to: {filtered_out_file}")
