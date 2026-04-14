import sys
import numpy as np
import pandas as pd


def encode_barcodes(barcodes):
    mapping = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
    arr = np.array([[mapping.get(c, 0) for c in bc] for bc in barcodes], dtype=np.uint8)
    return arr


def verify_barcodes(input_file, min_dist=2):
    df = pd.read_csv(input_file, sep='\t')
    if 'barcode' not in df.columns:
        print(f"No 'barcode' column found in {input_file}")
        sys.exit(1)
    barcodes = df['barcode'].dropna().tolist()
    n = len(barcodes)
    print(f"Loaded {n} barcodes from {input_file}")

    arr = encode_barcodes(barcodes)
    total_pairs = n * (n - 1) // 2
    print(f"Checking {total_pairs:,} pairs for Hamming distance >= {min_dist}...")

    violations = []
    next_milestone = 10

    for i in range(n):
        dists = np.sum(arr[i] != arr[i+1:], axis=1)
        bad = np.where(dists < min_dist)[0]
        for b in bad:
            j = i + 1 + int(b)
            violations.append((i, j, barcodes[i], barcodes[j], int(dists[b])))

        pairs_checked = i * n - i * (i + 1) // 2
        pct = (pairs_checked / total_pairs) * 100
        if pct >= next_milestone:
            print(f"  {int(next_milestone)}% complete")
            next_milestone += 10

    if violations:
        print(f"\nFAILED: {len(violations)} pairs violate minimum Hamming distance of {min_dist}:")
        for i, j, bc1, bc2, dist in violations[:20]:
            print(f"  [{i}] {bc1} vs [{j}] {bc2} -> distance {dist}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
    else:
        print(f"\nPASSED: All {total_pairs:,} pairs have Hamming distance >= {min_dist}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_barcodes_fast.py <input_file.txt>")
        sys.exit(1)
    verify_barcodes(sys.argv[1])
