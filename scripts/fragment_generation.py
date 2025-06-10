# scripts/fragment_generation.py
import pandas as pd
import os

# Constants
LEFT_PBS = "GACGTTCTCACAGCAATTCGTACAGTCGACGTCGATTCGTGT"
PROTO_CONST = "TTGACATTCTGCAATTA"
PAM_COST = "AGTATGTATGCTTCGCGCAGTGCGACTTCGCAGCGCATCACTTCA"
RIGHT_PBS = "AGAGCTGCGAGTCTTACAGCATTGC"

def generate_fragments(
    input_file=None,
    barcode_file="barcode_list.txt",
    output_file=None
):
    if input_file is None:
        dedup_file = "intermediate_files/4a_deduplicated_file_with_sequences.txt"
        fallback_file = "intermediate_files/3a_cleaned_file_with_sequences.txt"
        input_file = dedup_file if os.path.exists(dedup_file) else fallback_file

    if output_file is None:
        user_filename = input("Enter a name for the final oligo output file (without extension): ").strip()
        if not user_filename:
            raise ValueError("❌ Output filename cannot be empty.")
        if not user_filename.endswith(".txt"):
            user_filename += ".txt"
        output_file = os.path.join(os.getcwd(), user_filename)


    if not os.path.exists(input_file):
        raise FileNotFoundError(f"❌ Input file not found: {input_file}")
    
    if not os.path.exists(barcode_file):
        raise FileNotFoundError(f"❌ Barcode file not found: {barcode_file}")

    # Read data
    df = pd.read_csv(input_file, sep='\t')

    # Read and reverse barcodes
    with open(barcode_file, 'r') as f:
        barcodes = [line.strip() for line in f if line.strip()]
    barcodes.reverse()

    if len(barcodes) < len(df):
        raise ValueError("❌ Not enough barcodes for the number of rows in the input file.")

    # Assign barcodes
    df['Left_PBS'] = LEFT_PBS
    df['barcode'] = barcodes[:len(df)]
    df['proto_const'] = PROTO_CONST
    df['PAM_cost'] = PAM_COST
    df['barcode_2'] = df['barcode']
    df['Right_PBS'] = RIGHT_PBS

    # Reorder columns
    fetched_seq = df.pop('fetched_sequence')
    df.insert(df.columns.get_loc('proto_const') + 1, 'fetched_sequence', fetched_seq)

    # Generate oligo
    df['oligo'] = (
        df['Left_PBS'].astype(str) +
        df['barcode'].astype(str) +
        df['proto_const'].astype(str) +
        df['fetched_sequence'].astype(str) +
        df['PAM_cost'].astype(str) +
        df['barcode_2'].astype(str) +
        df['Right_PBS'].astype(str)
    )

    df.to_csv(output_file, sep='\t', index=False)
    print(f"Final annotated oligo file saved to: {output_file}")
