#scripts/select_variants.py
import pandas as pd

def select_variant_locations(input_file="intermediate_files/3a_cleaned_file_with_sequences.txt"):
    df = pd.read_csv(input_file, sep='\t')
    df.columns = [col.lower() for col in df.columns]
    filtered = df[(df["mismatches"] <= 1) & (df["bulge_size"] == 0)]

    if filtered.empty:
        print("No entries found with 1 (or 0) mismatch and 0 bulges.")
        return []
    
    print("\nEntries with 1 mismatch and 0 bulges:\n")
    print(filtered.to_string(index=False))

    df_filtered_mutations = df[~df["mutation"].str.endswith("_multi")]
    filtered_filtered_mutations = filtered[~filtered["mutation"].str.endswith("_multi")]

    all_mutations = df_filtered_mutations["mutation"].unique()
    filtered_mutations = filtered_filtered_mutations["mutation"].unique()

    missing_mutations = set(all_mutations) - set(filtered_mutations)
    if missing_mutations:
        print("\nWARNING: The following variants do NOT have any entries with <=1 mismatch and 0 bulges:")
        print(", ".join(missing_mutations))

    mutation_groups = filtered.groupby("mutation")
    selected_frag_numbs = []

    for mutation, group in mutation_groups:
        if len(group) == 1:
            print(f"\nSingle entry for variant {mutation}:\n")
            print(group.to_string(index=False))
            selected_frag_numbs.append(group.iloc[0]["frag_numb"])
        else:
            print(f"\nMultiple entries found for variant {mutation}:")
            for i, frag in enumerate(group["frag_numb"]):
                print(f"{i+1}. {frag}")

            while True:
                selection = input(f"Select the number corresponding to the frag_numb to process for variant {mutation}: ").strip()
                if selection.isdigit() and 1 <= int(selection) <= len(group):
                    selected_row = group.iloc[int(selection)-1]
                    selected_frag_numbs.append(selected_row["frag_numb"])
                    break
                else:
                    print("Invalid selection. Try again.")

    return selected_frag_numbs


