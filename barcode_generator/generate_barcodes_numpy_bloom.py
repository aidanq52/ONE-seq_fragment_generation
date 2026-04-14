import numpy as np
import os
import glob
from tqdm import tqdm
import mmh3  # For hashing (pip install mmh3)
from bitarray import bitarray  # For efficient bit storage (pip install bitarray)

# Constants
BASES = np.array(['A', 'C', 'G', 'T'])
BASE_TO_INT = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
INT_TO_BASE = {v: k for k, v in BASE_TO_INT.items()}
CHECKPOINT_FILE = "barcode_list.txt"

# Bloom filter parameters
BLOOM_SIZE = 100_000_000  # size of bit array (~12 MB memory)
NUM_HASHES = 7  # number of hash functions


class BloomFilter:
    def __init__(self, size=BLOOM_SIZE, num_hashes=NUM_HASHES):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray(size)
        self.bit_array.setall(False)

    def _hashes(self, item):
        item_bytes = item.encode('utf-8')
        for i in range(self.num_hashes):
            yield mmh3.hash(item_bytes, i) % self.size

    def add(self, item):
        for pos in self._hashes(item):
            self.bit_array[pos] = True

    def __contains__(self, item):
        return all(self.bit_array[pos] for pos in self._hashes(item))


BASES_STR = "ACGT"


def hamming_neighbors(seq):
    """Generate all sequences with Hamming distance 1 from seq."""
    neighbors = []
    for i in range(len(seq)):
        for base in BASES_STR:
            if base != seq[i]:
                neighbors.append(seq[:i] + base + seq[i+1:])
    return neighbors


def add_barcode_to_bloom(bloom, barcode):
    """Add a barcode and all its distance-1 neighbors to the bloom filter."""
    bloom.add(barcode)
    for neighbor in hamming_neighbors(barcode):
        bloom.add(neighbor)


def has_no_4_consecutive_same(bc):
    run_length = 1
    for i in range(1, len(bc)):
        if bc[i] == bc[i - 1]:
            run_length += 1
            if run_length > 4:
                return False
        else:
            run_length = 1
    return True


def load_checkpoint(filename):
    barcodes = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                bc = line.strip()
                if len(bc) == 14:
                    barcodes.append(bc)
        print(f"[⏩] Resumed from checkpoint with {len(barcodes)} barcodes")
    return barcodes


def append_to_checkpoint(filename, buffer):
    with open(filename, 'a') as f:
        for bc in buffer:
            f.write(bc + '\n')


def count_input_library_rows(input_dir="Input_libraries"):
    total_rows = 0
    for filepath in glob.glob(os.path.join(input_dir, "*.txt")):
        with open(filepath, 'r') as f:
            lines = sum(1 for line in f if line.strip())
        total_rows += lines - 1  # subtract header
    return total_rows


def generate_barcodes(n_barcodes=None, length=14, min_dist=2, checkpoint_every=200):
    if n_barcodes is None:
        n_barcodes = (count_input_library_rows())
        print(f"Counted {n_barcodes} rows across input library files.")
    barcodes = load_checkpoint(CHECKPOINT_FILE)
    bloom = BloomFilter()

    # Rebuild bloom filter with loaded barcodes (including neighbors for hamming distance)
    for bc in barcodes:
        add_barcode_to_bloom(bloom, bc)

    pbar = tqdm(total=n_barcodes, initial=len(barcodes), desc="Generating barcodes")
    buffer = []

    while len(barcodes) < n_barcodes:
        candidate_array = np.random.randint(0, 4, size=length)
        candidate = ''.join(BASES[candidate_array])

        if not has_no_4_consecutive_same(candidate):
            continue

        # Check Bloom filter (probabilistic membership)
        if candidate in bloom:
            continue  # Probably too close to existing barcode

        # Accept candidate
        barcodes.append(candidate)
        add_barcode_to_bloom(bloom, candidate)
        buffer.append(candidate)
        pbar.update(1)

        if len(buffer) >= checkpoint_every:
            append_to_checkpoint(CHECKPOINT_FILE, buffer)
            buffer.clear()

    if buffer:
        append_to_checkpoint(CHECKPOINT_FILE, buffer)

    pbar.close()
    return barcodes


def main():
    generate_barcodes(n_barcodes=2000000)


if __name__ == "__main__":
    main()
