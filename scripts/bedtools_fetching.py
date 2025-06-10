# scripts/bedtools_fetching.py
import pandas as pd
import subprocess
import os

def fetch_sequences_with_bedtools(
    input_file='intermediate_files/2a_combined_library_cleaned.txt',
    fasta_file='hg38.fa',
    output_file='intermediate_files/3a_cleaned_file_with_sequences.txt'
):
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    if not os.path.exists(fasta_file):
        print(f"❌ FASTA file not found: {fasta_file}")
        return

    df = pd.read_csv(input_file, sep='\t')

    # Create BED dataframe
    bed_df = pd.DataFrame()
    bed_df['chrom'] = df['Chromosome']
    bed_df['start'] = df['Location'].astype(int) - 10
    bed_df['end'] = df['Location'].astype(int) + 33
    bed_df['name'] = df['Frag_numb']
    bed_df['score'] = 0
    bed_df['strand'] = df['Direction']

    bed_file = 'intermediate_files/3b_temp.bed'
    bed_df.to_csv(bed_file, sep='\t', header=False, index=False)

    # Run bedtools
    temp_fasta_output = 'intermediate_files/3c_temp_fasta_output.txt'
    cmd = [
        'bedtools', 'getfasta',
        '-fi', fasta_file,
        '-bed', bed_file,
        '-tab',
        '-name',
        '-s',
    ]

    print("Running bedtools getfasta...")
    with open(temp_fasta_output, 'w') as out:
        subprocess.run(cmd, stdout=out, check=True)
    print("bedtools finished.")

    # Parse results
    fetched_seqs = {}
    with open(temp_fasta_output) as f:
        for line in f:
            name, seq = line.strip().split('\t')
            frag_numb = name.split('::')[0]
            fetched_seqs[frag_numb] = seq

    df['fetched_sequence'] = df['Frag_numb'].map(fetched_seqs)

    # Save final result
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, sep='\t', index=False)
    print(f"Fetched sequences written to: {output_file}")
