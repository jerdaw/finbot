import pandas as pd
from tqdm import tqdm


def avg_stepped_results(results: pd.DataFrame) -> pd.DataFrame:
    all_cols = list(results.columns)
    cols_to_check = all_cols[all_cols.index("Stocks") : all_cols.index("Starting Value") + 1]
    entries: dict[tuple, list] = {}
    for _r_idx, row in tqdm(results.iterrows(), desc="Parsing test results", total=len(results)):
        hash_vals = tuple(row.loc[cols_to_check])
        entries.setdefault(hash_vals, []).append(row)

    averaged = []
    for _hash_vals, rows in tqdm(entries.items(), desc="Averaging test step results", total=len(entries)):
        merged = pd.DataFrame(rows)
        cols_pre_check = pd.Series(
            {
                "Start Date": merged["Start Date"].min(),
                "End Date": merged["End Date"].max(),
                "Duration": merged["Duration"].mean().round(freq="s"),
                "# Stepped Tests": len(merged),
            }
        )
        checked_cols = merged[cols_to_check].iloc[0]
        cols_post_check = pd.Series(
            {col_h: merged[col_h].mean() for col_h in all_cols[all_cols.index(cols_to_check[-1]) + 1 :]}
        )
        averaged_test = pd.concat((cols_pre_check, checked_cols, cols_post_check), axis=0)
        averaged.append(averaged_test)

    return pd.DataFrame(averaged).reset_index(drop=True)
