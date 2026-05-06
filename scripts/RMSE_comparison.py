import math
import pandas as pd
import numpy as np

# =====================================================
# 1. Load Excel file (Rensad_lista)
# =====================================================

excel_path = "year_comparisons.xlsx"

df = pd.read_excel(excel_path, sheet_name="Rensad_lista")


# Quick sanity check
print("Columns:", df.columns.tolist())
print("Number of rows:", len(df))


# 2. Define reference columns (LIBRIS)
REF_START_COL = "Libris_start"
REF_END_COL   = "Libris_end"

# 3. Define the models and their start/end columns
models = {
    "Claude":  ("Claude_Start",  "Claude_End"),
    "Gpt":     ("Gpt_Start",     "Gpt_End"),
    "Mistral": ("Mistral_Start", "Mistral_End"),
    "Llama":   ("Llama_Start",   "Llama_End"),
}

# 4. Helper: per-novel RMSE as in your formula
def rmse_per_novel(pred_start, pred_end, ref_start, ref_end):
    """
    RMSE_novel_i = sqrt( ((predStart_i - refStart_i)^2 + (predEnd_i - refEnd_i)^2) / 2 )
    Computed elementwise over the whole column.
    """
    return np.sqrt(((pred_start - ref_start) ** 2 + (pred_end - ref_end) ** 2) / 2)

# 5. Loop over each model and compute the metrics
overall_results = {}

for model_name, (start_col, end_col) in models.items():
    # --- (a) Per-novel RMSE (row-wise) ---
    rmse_col_name = f"RMSE_{model_name}_novel"
    df[rmse_col_name] = rmse_per_novel(
        df[start_col],
        df[end_col],
        df[REF_START_COL],
        df[REF_END_COL]
    )

    # --- (b) Overall RMSE for all start years (across N novels) ---
    start_errors = df[start_col] - df[REF_START_COL]
    rmse_start = np.sqrt(np.nanmean(start_errors ** 2))

    # --- (c) Overall RMSE for all end years (across N novels) ---
    end_errors = df[end_col] - df[REF_END_COL]
    rmse_end = np.sqrt(np.nanmean(end_errors ** 2))

    overall_results[model_name] = {
        "RMSE_start": rmse_start,
        "RMSE_end": rmse_end,
    }

# 6. Print overall RMSE per model
for model_name, res in overall_results.items():
    print(
        f"{model_name}: "
        f"RMSE_start = {res['RMSE_start']:.3f}, "
        f"RMSE_end = {res['RMSE_end']:.3f}"
    )

# 7. (Optional) Save the dataframe with the new RMSE columns
df.to_excel("year_comparisons_with_rmse.xlsx", sheet_name="Rensad_lista", index=False)