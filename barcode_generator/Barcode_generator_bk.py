import os
from tqdm import tqdm

# Constants for base encoding
BASE_TO_BITS = {'A': 0b00, 'C': 0b01, 'G': 0b10, 'T': 0b11}
BITS_TO_BASE = {v: k for k, v in BASE_TO_BITS.items()}


def encode_barcode(barcode):
    val = 0
    for base in barcode:
        val = (val << 2) | BASE_TO_BITS[base]
    return val


def decode_barcode(val, length=14):
    bases = []
    for _ in range(length):
        bits = val & 0b11
        bases.append(BITS_TO_BASE[bits])
        val >>= 2
    return ''.join(reversed(bases))


def hamming_distance_encoded(x, y, length=14):
    diff = x ^ y
    count = 0
    for _ in range(length):
        if (diff & 0b11) != 0:
            count += 1
        diff >>= 2
    return count


class BKTreeNode:
    def __init__(self, value):
        self.value = value
        self.children = {}

    def insert(self, candidate, dist_func, length):
        distance = dist_func(candidate, self.value, length)
        if distance in self.children:
            self.children[distance].insert(candidate, dist_func, length)
        else:
            self.children[distance] = BKTreeNode(candidate)

    def search(self, target, max_dist, dist_func, length):
        distance = dist_func(target, self.value, length)
        if distance < max_dist:
            return False
        for d in range(distance - max_dist, distance + max_dist + 1):
            child = self.children.get(d)
            if child and not child.search(target, max_dist, dist_func, length):
                return False
        return True


def increment_barcode(barcode):
    bases = ['A', 'C', 'G', 'T']
    base_to_idx = {b: i for i, b in enumerate(bases)}
    idx_to_base = {i: b for i, b in enumerate(bases)}
    chars = list(barcode)
    pos = len(chars) - 1
    while pos >= 0:
        current_idx = base_to_idx[chars[pos]]
        if current_idx == 3:
            chars[pos] = 'A'
            pos -= 1
        else:
            chars[pos] = idx_to_base[current_idx + 1]
            break
    if pos < 0:
        return None
    return ''.join(chars)


def generate_barcodes(n, length=14, min_distance=2, checkpoint_file='barcode_list.txt', checkpoint_every=500):
    barcodes = []
    encoded_barcodes = []
    seen = set()
    bk_tree = None

    candidate = 'A' * length

    # Resume from checkpoint
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            for line in f:
                bc = line.strip()
                if len(bc) == length:
                    barcodes.append(bc)
                    enc = encode_barcode(bc)
                    encoded_barcodes.append(enc)
                    seen.add(bc)
                    if bk_tree is None:
                        bk_tree = BKTreeNode(enc)
                    else:
                        bk_tree.insert(enc, hamming_distance_encoded, length)
        if barcodes:
            candidate = increment_barcode(barcodes[-1])
        print(f"[⏩] Resuming from checkpoint with {len(barcodes)} barcodes...")

    pbar = tqdm(total=n, initial=len(barcodes), desc="Generating barcodes")
    buffer = []

    while candidate is not None and len(barcodes) < n:
        if candidate in seen:
            candidate = increment_barcode(candidate)
            continue

        encoded = encode_barcode(candidate)

        if bk_tree is None or bk_tree.search(encoded, min_distance, hamming_distance_encoded, length):
            barcodes.append(candidate)
            encoded_barcodes.append(encoded)
            seen.add(candidate)
            buffer.append(candidate)

            if bk_tree is None:
                bk_tree = BKTreeNode(encoded)
            else:
                bk_tree.insert(encoded, hamming_distance_encoded, length)

            pbar.update(1)

            # Save checkpoint
            if len(buffer) >= checkpoint_every:
                with open(checkpoint_file, 'a') as f:
                    f.write('\n'.join(buffer) + '\n')
                buffer.clear()

        candidate = increment_barcode(candidate)

    # Final save
    if buffer:
        with open(checkpoint_file, 'a') as f:
            f.write('\n'.join(buffer) + '\n')

    pbar.close()

    if len(barcodes) < n:
        print(f"[⚠️] Only {len(barcodes)} barcodes generated (end of space).")
    else:
        print(f"[✓] Successfully generated {len(barcodes)} barcodes.")

    return barcodes


def main():
    generate_barcodes(
        n=300000,
        length=14,
        min_distance=2,
        checkpoint_file='barcode_list.txt',
        checkpoint_every=500
    )


if __name__ == "__main__":
    main()
