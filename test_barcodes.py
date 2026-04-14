import sys
import pandas as pd

def hamming_distance(a, b):
    return sum(c1 != c2 for c1, c2 in zip(a, b))


def verify_barcodes(input_file, min_dist=2):
    df = pd.read_csv(input_file, sep='\t')
    if 'barcode' not in df.columns:
        print(f"No 'barcode' column found in {input_file}")
        sys.exit(1)
    barcodes = df['barcode'].dropna().tolist()

    print(f"Loaded {len(barcodes)} barcodes from {input_file}")

    violations = []
    total_pairs = len(barcodes) * (len(barcodes) - 1) // 2

    print(f"Checking {total_pairs} pairs for Hamming distance >= {min_dist}...")

    pairs_checked = 0
    next_milestone = 10

    for i in range(len(barcodes)):
        for j in range(i + 1, len(barcodes)):
            dist = hamming_distance(barcodes[i], barcodes[j])
            if dist < min_dist:
                violations.append((i, j, barcodes[i], barcodes[j], dist))
            pairs_checked += 1

        pct = (pairs_checked / total_pairs) * 100
        if pct >= next_milestone:
            print(f"  {int(next_milestone)}% complete ({pairs_checked}/{total_pairs} pairs)")
            next_milestone += 10

    if violations:
        print(f"\nFAILED: {len(violations)} pairs violate minimum Hamming distance of {min_dist}:")
        for idx, (i, j, bc1, bc2, dist) in enumerate(violations[:20]):
            print(f"  [{i}] {bc1} vs [{j}] {bc2} -> distance {dist}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
    else:
        print(f"\nPASSED: All {total_pairs} pairs have Hamming distance >= {min_dist}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_barcodes.py <input_file.txt>")
        sys.exit(1)
    verify_barcodes(sys.argv[1])
