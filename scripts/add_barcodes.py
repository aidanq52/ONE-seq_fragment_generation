import csv

def add_barcodes_to_library(
    barcodes_file='barcode_list.txt',
    input_file='combined_library_cleaned.txt',
    output_file='combined_library_with_barcodes.txt'
):
    # Read barcodes and reverse the list
    with open(barcodes_file, 'r') as f:
        barcodes = [line.strip() for line in f if line.strip()]
    barcodes.reverse()

    # Read the input library
    with open(input_file, 'r') as infile:
        reader = list(csv.reader(infile, delimiter='\t'))
        header = reader[0]
        rows = reader[1:]

    # Sanity check: Ensure enough barcodes are available
    if len(barcodes) < len(rows):
        raise ValueError("Not enough barcodes for the number of rows in the library.")

    # Add new header
    header.append('barcode')

    # Add barcodes to each row
    new_rows = [row + [barcodes[i]] for i, row in enumerate(rows)]

    # Write the output file
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(header)
        writer.writerows(new_rows)

    print(f"Barcodes added. Output saved to: {output_file}")
