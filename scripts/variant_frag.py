# scripts/filter_one_mismatch.py
import pandas as pd

def print_single_mismatch(input_file="intermediate_files/4a_deduplicated_file_with_sequences.txt",
                          output_file="intermediate_files/5a_pre_barcode_plus_variants.txt"):

    """
    Reads the deduplicated file and prints entries with 1 mismatch and 0 bulges.
    """
    # Load the TSV
    df = pd.read_csv(input_file, sep="\t")

    # Filter for 1 mismatch and 0 bulges
    filtered = df[(df["mismatches"] == 1) & (df["bulge_size"] == 0)]

    # Print to console
    if filtered.empty:
        print("No entries found with 1 mismatch and 0 bulges.")
    else:
        print("\nEntries with 1 mismatch and 0 bulges:\n")
        print(filtered.to_string(index=False))

    while True:
        confirm = input("\nAre these the on-target sites? (y/n): ").strip().lower()

        if confirm == "y":
            variants = []
            for idx, row in enumerate(filtered.itertuples(index=False)):
                new_row = row._asdict()

                # Replace ID (first column)
                first_col_name = df.columns[0]
                new_row[first_col_name] = f"{chr(65 + idx)}-variant"

                # Reset mismatches to 0
                new_row["mismatches"] = 0

                # Correct mismatch in dna
                cr = new_row["crrna"]
                dn = list(new_row["dna"])
                mismatch_index = next((j for j, (a, b) in enumerate(zip(cr, dn)) if a != b), None)
                if mismatch_index is None:
                    raise ValueError(f"No mismatch found for row {row}")
                
                # Fix dna sequence
                dn[mismatch_index] = cr[mismatch_index]
                new_row["dna"] = "".join(dn)

                # Fix fetched_sequence at offset (11th base = index 10)
                fs = list(new_row["fetched_sequence"])
                fetch_index = mismatch_index + 10
                if fetch_index >= len(fs):
                    raise ValueError(f"Mismatch index {fetch_index} out of range for fetched_sequence")
                fs[fetch_index] = cr[mismatch_index]
                new_row["fetched_sequence"] = "".join(fs)

                variants.append(new_row)

            # Combine variants with original
            combined = pd.concat([pd.DataFrame(variants), df], ignore_index=True)

            # Print original + modified for user
            print("\nOriginal and modified entries:\n")
            display_df = pd.concat([filtered, pd.DataFrame(variants)], ignore_index=True)
            print(display_df.to_string(index=False))

            # Save to file
            combined.to_csv(output_file, sep="\t", index=False)
            print(f"\nVariants prepended to file and saved as:\n{output_file}")
            break

        elif confirm == "n":
            print("Operation cancelled by user. No changes made.")
            break

        else:
            print("Invalid input. Please enter 'y' or 'n'.")
