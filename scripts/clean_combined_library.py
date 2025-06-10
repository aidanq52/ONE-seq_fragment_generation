# scripts/clean_combined_library.py
import pandas as pd
import os

def clean_combined_library(
    input_file='./intermediate_files/1a_combined_library_messy.txt',
    output_file='./intermediate_files/2a_combined_library_cleaned.txt'
):
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    df = pd.read_csv(input_file, sep='\t', dtype=str)

    # Drop specified columns if they exist
    columns_to_drop = ['ID', 'Selected/removed', 'Removed_IDs']
    df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

    # Save cleaned version
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, sep='\t', index=False)

    print(f"Cleaned file written to: {output_file}")
