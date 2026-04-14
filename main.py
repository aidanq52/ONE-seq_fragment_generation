# main.py
from scripts.combine_libraries import combine_libraries
from scripts.clean_combined_library import clean_combined_library
from scripts.bedtools_fetching import fetch_sequences_with_bedtools
from scripts.select_variants import select_variant_locations
from scripts.dedup import deduplicate_sequences
from scripts.multi_site_report import generate_multi_site_report
from scripts.create_variants import create_variant_entries
from scripts.fragment_generation import generate_fragments
from barcode_generator.generate_barcodes_numpy_bloom import generate_barcodes
import os

def main():
    print("File Set Up")
    gen_barcodes = input("Would you like to run the 'Generate Barcode'? \n" \
                         " If you have not generated barcodes for this libary before\n" \
                         " it is recommended that you run the generation script.\n" \
                         " Generate new barcodes? (y/n): ").strip().lower()  
    if gen_barcodes in {"y", "yes"}:
        if os.path.exists("barcode_list.txt"):
            os.remove("barcode_list.txt")
        generate_barcodes()


    print(" Step 1: Combining library files...")
    combine_libraries()

    print("\n Step 2: Cleaning combined library...")
    clean_combined_library()

    print("\n Step 3: Fetching sequences with bedtools...")
    fetch_sequences_with_bedtools(fasta_file='/root/hg38.fa')

    print("\n Step 4: Selecting variant locations...")
    selected_frag_numbs = select_variant_locations()

    print("\n Step 5: Deduplicating sequences...")
    deduplicate_sequences(priority_frag_numbs=selected_frag_numbs)

    print("\n Step 5b: Generating multi-site report...")
    generate_multi_site_report()

    print("\n Step 6: Creating variant entries...")
    create_variant_entries(selected_frag_numbs)

    print("\n Step 7: Adding constant regions & barcodes...")
    generate_fragments()


if __name__ == "__main__":
    main()