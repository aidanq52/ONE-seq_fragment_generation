# scripts/combine_libraries.py
import pandas as pd
import glob
import os
import string
import re

def combine_libraries(input_dir='./Input_libraries/', output_dir='./intermediate_files/'):
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, '1a_combined_library_messy.txt')

    file_paths = sorted(glob.glob(os.path.join(input_dir, '*.txt')))
    if not file_paths:
        print("No .txt files found in the input directory.")
        return

    dfs = []
    entry_counts = {}
    total_entries = 0
    start_number = 100000
    mutation_pattern = re.compile(r'[A-Z]\d+[A-Z]')

    for i, file_path in enumerate(file_paths):
        prefix = string.ascii_uppercase[i]
        filename = os.path.basename(file_path)

        tokens = re.split(r'[_\-]', filename)
        candidates = [tok for tok in tokens if mutation_pattern.fullmatch(tok)]
        mutation_name = candidates[0] if candidates else ""
        print(f"\nProcessing file: {filename}")
        while True:
            if mutation_name:
                print(f"Detected mutation name: {mutation_name}")
                user_input = input("Press [Enter] to confirm or type a different name: ").strip()
                if user_input:
                    mutation_name = user_input
                break
            else:
                mutation_name = input("Could not detect mutation name. Please enter one: ").strip()
                if mutation_name:
                    break


        df = pd.read_csv(file_path, sep='\t', dtype=str)
        id_column = 'ID'
        frag_ids = [f"{prefix}{row[id_column]}" for _, row in df.iterrows()]
        df.insert(0, 'Frag_numb', frag_ids)
        df.insert(1, 'mutation', mutation_name)

        entry_counts[mutation_name] = len(df)
        total_entries += len(df)
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(output_file, sep='\t', index=False)

    print(f"\nCombined file written to: {output_file}")
    print(f"Total entries: {total_entries}")
    print("\nEntries per mutation:")
    for mutation, count in entry_counts.items():
        print(f" - {mutation}: {count}")
