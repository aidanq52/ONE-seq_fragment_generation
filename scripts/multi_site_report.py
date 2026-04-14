# scripts/multi_site_report.py
import pandas as pd
import os


def generate_multi_site_report(
    kept_file="intermediate_files/4a_deduplicated_file_with_sequences.txt",
    removed_file="intermediate_files/4b_deduplicated_removed_entries.txt",
    output_file="intermediate_files/4c_multi_site_report.csv",
):
    if not os.path.exists(kept_file):
        print(f"Skipping multi-site report: {kept_file} not found.")
        return
    if not os.path.exists(removed_file):
        print(f"Skipping multi-site report: {removed_file} not found.")
        return

    kept = pd.read_csv(kept_file, sep="\t", dtype=str)
    removed = pd.read_csv(removed_file, sep="\t", dtype=str)

    if "kept_frag_numb" not in removed.columns:
        print("Skipping multi-site report: 'kept_frag_numb' column missing from removed file.")
        return

    # Index kept fragments by frag_numb for fast lookup
    kept_index = kept.set_index("frag_numb")

    # Only report reference fragments that actually have duplicates
    ref_frag_numbs = removed["kept_frag_numb"].unique()

    rows = []
    for ref_frag in ref_frag_numbs:
        if ref_frag not in kept_index.index:
            continue
        ref = kept_index.loc[ref_frag]

        # Reference row
        rows.append({
            "role": "reference",
            "frag_numb": ref_frag,
            "mutation": ref["mutation"],
            "chromosome": ref.get("chromosome", ""),
            "location": ref.get("location", ""),
            "direction": ref.get("direction", ""),
            "mismatches": ref.get("mismatches", ""),
            "bulge_size": ref.get("bulge_size", ""),
            "fetched_sequence": ref.get("fetched_sequence", ""),
        })

        # Duplicate rows deduplicated to this reference
        dupes = removed[removed["kept_frag_numb"] == ref_frag]
        for _, dupe in dupes.iterrows():
            rows.append({
                "role": "duplicate",
                "frag_numb": dupe["frag_numb"],
                "mutation": dupe["mutation"],
                "chromosome": dupe.get("chromosome", ""),
                "location": dupe.get("location", ""),
                "direction": dupe.get("direction", ""),
                "mismatches": dupe.get("mismatches", ""),
                "bulge_size": dupe.get("bulge_size", ""),
                "fetched_sequence": dupe.get("fetched_sequence", ""),
            })

    report = pd.DataFrame(rows)
    report.to_csv(output_file, index=False)
    print(f"Multi-site report saved to: {output_file}")
    print(f"  {len(ref_frag_numbs)} reference fragments with {len(removed)} total duplicates.")
