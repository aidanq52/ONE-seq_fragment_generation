import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Input file
input_file = "Xi_g6_g7_g8-NNN_ONE-seq_Library.txt"

# Load data
df = pd.read_csv(input_file, sep="\t")

# Normalize mutation column (strip _multi)
df["mutation_normalized"] = df["mutation"].astype(str).str.replace(r"_multi$", "", regex=True)

# Determine max sequence length to set histogram bins
max_len = df["dna"].dropna().str.len().max()
bins = range(1, max_len + 2)  # 1-based positions

# --- Helper function to collect positions ---
def collect_positions(df, char_check):
    pos_dict = defaultdict(list)  # mutation -> list of positions
    for mut, group in df.groupby("mutation_normalized"):
        for seq in group["dna"].dropna():
            for i, c in enumerate(seq, start=1):
                if char_check(c):
                    pos_dict[mut].append(i)
    return pos_dict

# --- Collect positions ---
dash_positions_by_mut = collect_positions(df, lambda c: c == "-")
lowercase_positions_by_mut = collect_positions(df, lambda c: c.islower())

# --- Plot function ---
def plot_stacked_histogram(pos_dict, title, output_file, color_map=None):
    if not pos_dict:
        print(f"No data for {title}")
        return

    plt.figure(figsize=(12, 6))
    all_mutations = list(pos_dict.keys())
    counts_matrix = []

    # Build counts for each mutation
    for mut in all_mutations:
        counts, _ = np.histogram(pos_dict[mut], bins=bins)
        counts_matrix.append(counts)

    # Stack bars
    bottoms = np.zeros(len(bins) - 1)
    colors = plt.cm.tab20.colors  # color palette
    for i, counts in enumerate(counts_matrix):
        plt.bar(bins[:-1], counts, bottom=bottoms,
                width=1.0, align="edge", label=all_mutations[i],
                color=colors[i % len(colors)])
        bottoms += counts

    plt.title(title)
    plt.xlabel("Position in DNA sequence (1-based)")
    plt.ylabel("Count")
    plt.legend(title="Mutation", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")

import numpy as np

# --- Plot dash histogram ---
plot_stacked_histogram(dash_positions_by_mut,
                       "Dash '-' Positions in DNA Sequences by Mutation",
                       "dna_dash_positions_stacked_by_mutation.png")

# --- Plot lowercase histogram ---
plot_stacked_histogram(lowercase_positions_by_mut,
                       "Lowercase Letter Positions in DNA Sequences by Mutation",
                       "dna_lowercase_positions_stacked_by_mutation.png")
