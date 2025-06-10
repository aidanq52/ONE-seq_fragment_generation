# main.py
from scripts.combine_libraries import combine_libraries
from scripts.clean_combined_library import clean_combined_library
from scripts.bedtools_fetching import fetch_sequences_with_bedtools
from scripts.dedup import deduplicate_sequences
from scripts.fragment_generation import generate_fragments

def main():
    print(" Step 1: Combining library files...")
    combine_libraries()

    print("\n Step 2: Cleaning combined library...")
    clean_combined_library()

    print("\n Step 3: Fetching sequences with bedtools...")
    fetch_sequences_with_bedtools(fasta_file='hg38.fa')

    print("\n Step 4: Deduplicating sequences...")
    deduplicate_sequences()

    print("\n Step 5: adding constant regions & barcodes...")
    generate_fragments()


if __name__ == "__main__":
    main()