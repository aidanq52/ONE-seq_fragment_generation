import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_FILE = "Alpha_ML38_20260329.txt"
OUTPUT_FILE = "Alpha_ML38_20260329_data_checks.png"

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_FILE, sep="\t", low_memory=False)
df.columns = df.columns.str.strip().str.lower()

# Normalise mutation (strip _multi suffix for grouping)
df["mutation_base"] = df["mutation"].astype(str).str.replace(r"_multi$", "", regex=True)
df["is_multi"]      = df["mutation"].astype(str).str.endswith("_multi")

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 18))
fig.patch.set_facecolor("#f0f8ff")

# Title banner
fig.text(0.5, 0.97, "Data Checks",
         ha="center", va="top", fontsize=28, fontweight="bold", color="white",
         bbox=dict(facecolor="#00aaff", edgecolor="none", boxstyle="round,pad=0.4"))

gs = gridspec.GridSpec(3, 2, figure=fig,
                       top=0.91, bottom=0.06,
                       hspace=0.45, wspace=0.35,
                       left=0.07, right=0.97)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])
ax4 = fig.add_subplot(gs[2, 0])
ax5 = fig.add_subplot(gs[2, 1])

panel_bg = "#e8f4fd"
for ax in [ax1, ax2, ax3, ax4, ax5]:
    ax.set_facecolor(panel_bg)

# ── Graph 1 – Stacked bar: non-multi (bottom) + multi (top) per variant ───────
base_mutations = sorted(df["mutation_base"].unique())
non_multi_counts = [df[(df["mutation_base"] == m) & (~df["is_multi"])].shape[0] for m in base_mutations]
multi_counts     = [df[(df["mutation_base"] == m) &   df["is_multi"]].shape[0]  for m in base_mutations]

x = range(len(base_mutations))
bars_non = ax1.bar(x, non_multi_counts, color="#5b9bd5", label="non-multi")
bars_mul  = ax1.bar(x, multi_counts, bottom=non_multi_counts, color="#ed7d31", label="multi")

ax1.set_xticks(x)
ax1.set_xticklabels(base_mutations, rotation=35, ha="right", fontsize=8)
ax1.set_title("Counts per Mutation Type", fontsize=11, fontweight="bold")
ax1.set_ylabel("Count")
ax1.legend(fontsize=8)

# Label total on top of each bar
for i, (nm, m) in enumerate(zip(non_multi_counts, multi_counts)):
    total = nm + m
    ax1.text(i, total + max(nm + m2 for nm, m2 in zip(non_multi_counts, multi_counts)) * 0.01,
             str(total), ha="center", va="bottom", fontsize=7)

# ── Graph 2 – RNA vs DNA Bulges ───────────────────────────────────────────────
bulge_counts = df["bulge_type"].value_counts().reindex(["RNA", "DNA", "X"], fill_value=0)
bulge_colors = ["#6495ed", "#cd5c5c", "#aaaaaa"]

bars2 = ax2.bar(bulge_counts.index, bulge_counts.values, color=bulge_colors)
ax2.set_title("Count of RNA vs DNA Bulges", fontsize=11, fontweight="bold")
ax2.set_ylabel("Count")

for bar, v in zip(bars2, bulge_counts.values):
    ax2.text(bar.get_x() + bar.get_width() / 2, v + max(bulge_counts.values) * 0.01,
             str(v), ha="center", va="bottom", fontsize=9)

# ── Graph 3 – Normalized frequency per chromosome by mismatch/bulge type ──────
df["mut_type"] = "m" + df["mismatches"].astype(str) + "_b" + df["bulge_size"].astype(str)

# hg38 chromosome sizes (bp)
hg38_sizes = {
    "chr1": 248956422, "chr2": 242193529, "chr3": 198295559, "chr4": 190214555,
    "chr5": 181538259, "chr6": 170805979, "chr7": 159345973, "chr8": 145138636,
    "chr9": 138394717, "chr10": 133797422, "chr11": 135086622, "chr12": 133275309,
    "chr13": 114364328, "chr14": 107043718, "chr15": 101991189, "chr16": 90338345,
    "chr17": 83257441, "chr18": 80373285, "chr19": 58617616, "chr20": 64444167,
    "chr21": 46709983, "chr22": 50818468, "chrX": 156040895, "chrY": 57227415,
}

# Define a fixed order for chromosomes
chrom_order = ([f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"])
chrom_order = [c for c in chrom_order if c in df["chromosome"].unique()]
chrom_sizes_bp = np.array([hg38_sizes.get(c, 1) for c in chrom_order])

mut_type_order = sorted(df["mut_type"].unique(),
                        key=lambda x: (int(x.split("_b")[1]),
                                       int(x.split("m")[1].split("_")[0])))

palette = plt.cm.tab10.colors
color_map = {mt: palette[i % len(palette)] for i, mt in enumerate(mut_type_order)}

bottoms = np.zeros(len(chrom_order))
for mt in mut_type_order:
    sub = df[df["mut_type"] == mt]
    counts = np.array([sub[sub["chromosome"] == c].shape[0] for c in chrom_order])
    normalized = counts / chrom_sizes_bp
    ax3.bar(range(len(chrom_order)), normalized, bottom=bottoms,
            color=color_map[mt], label=mt, width=0.8)
    bottoms += normalized

ax3.set_xticks(range(len(chrom_order)))
ax3.set_xticklabels([c.replace("chr", "") for c in chrom_order], fontsize=8)
ax3.set_xlabel("Chromosome")
ax3.set_ylabel("Fragments / bp")
ax3.set_title("Fragments per bp per Chromosome by Mismatch/Bulge Type",
              fontsize=11, fontweight="bold")
ax3.legend(title="Type", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=7)

# ── Graph 4 – Forward vs Reverse fragment distribution ────────────────────────
dir_counts = df["direction"].value_counts().reindex(["+", "-"], fill_value=0)
dir_labels = ["Forward (+)", "Reverse (-)"]
dir_colors = ["#5b9bd5", "#ed7d31"]

bars4 = ax4.bar(dir_labels, dir_counts.values, color=dir_colors, width=0.5)
for bar, v in zip(bars4, dir_counts.values):
    ax4.text(bar.get_x() + bar.get_width() / 2, v + max(dir_counts.values) * 0.01,
             str(v), ha="center", va="bottom", fontsize=10)

ax4.set_ylabel("Count")
ax4.set_title("Forward vs Reverse Fragments", fontsize=11, fontweight="bold")

# ── Graph 5 – Distribution of mismatch positions (lowercase in dna col) ───────
mismatch_positions = []
for seq in df["dna"].dropna().astype(str):
    for i, c in enumerate(seq):
        if c.islower():
            mismatch_positions.append(i)

if mismatch_positions:
    max_pos = max(mismatch_positions)
    counts5, edges5 = np.histogram(mismatch_positions, bins=range(0, max_pos + 2))
    ax5.bar(edges5[:-1], counts5, color="#5b9bd5", width=0.8, align="edge")
else:
    ax5.text(0.5, 0.5, "No mismatches found", ha="center", transform=ax5.transAxes)

ax5.set_xlabel("Position in Sequence")
ax5.set_ylabel("Count")
ax5.set_title("Distribution of Mismatch Positions", fontsize=11, fontweight="bold")

# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_FILE}")
