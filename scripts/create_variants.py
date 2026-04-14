# scripts/create_variants.py
import pandas as pd

def create_variant_entries(selected_frag_numbs,
                           input_file="intermediate_files/4a_deduplicated_file_with_sequences.txt",
                           output_file="intermediate_files/5a_pre_barcode_plus_variants.txt"):

    df = pd.read_csv(input_file, sep="\t")

    # Look up the selected entries by frag_numb
    variants_to_process = df[df["frag_numb"].isin(selected_frag_numbs)]

    if variants_to_process.empty:
        print("WARNING: None of the selected variant frag_numbs were found in the deduplicated file.")
        df.to_csv(output_file, sep="\t", index=False)
        return

    # Generate corrected variants
    variants = []
    for idx, row in enumerate(variants_to_process.itertuples(index=False)):
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

        dn[mismatch_index] = cr[mismatch_index]
        new_row["dna"] = "".join(dn)

        # Correct fetched_sequence at offset (11th base = index 10)
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
    display_df = pd.concat([variants_to_process, pd.DataFrame(variants)], ignore_index=True)
    print(display_df.to_string(index=False))

    # Save to file
    combined.to_csv(output_file, sep="\t", index=False)
    print(f"\nVariants prepended to file and saved as:\n{output_file}")