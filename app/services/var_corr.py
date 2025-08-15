import pandas as pd
import numpy as np
from app.services.data_loader import process_raw_data

def compute_var_correlation(categories=None, exclude=None):
    categories = categories or ["electricity", "naturalGas", "indexEnergy", "dieselValue"]
    exclude = exclude or []

    dfs = [
        process_raw_data(column_name=cat).rename(columns={'y': cat})[['ds', cat]]
        for cat in categories if cat not in exclude
    ]
    if not dfs:
        return {"error": "No valid data to compute correlation"}

    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='ds', how='outer')

    merged_df = merged_df.dropna()
    if merged_df.empty:
        return {"error": "No valid data to compute correlation"}

    # Compute correlations
    data = merged_df.drop(columns=['ds'])
    corr_methods = {m: data.corr(method=m) for m in ['spearman', 'pearson']}

    def get_top_correlation(corr_matrix):
        corr_vals = corr_matrix.where(~np.eye(len(corr_matrix), dtype=bool)).stack()
        if corr_vals.empty:
            return {"highest_positive": None, "highest_negative": None}
        top_pos = corr_vals.idxmax()
        top_neg = corr_vals.idxmin()
        return {
            "highest_positive": {"pair": list(top_pos), "value": float(corr_matrix.loc[top_pos])},
            "highest_negative": {"pair": list(top_neg), "value": float(corr_matrix.loc[top_neg])}
        }

    return {
        "spearman": {
            "matrix": corr_methods['spearman'].round(3).to_dict(),
            "insight": get_top_correlation(corr_methods['spearman'])
        },
        "pearson": {
            "matrix": corr_methods['pearson'].round(3).to_dict(),
            "insight": get_top_correlation(corr_methods['pearson'])
        }
    }
