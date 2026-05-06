import pandas as pd
from sklearn.metrics import f1_score, mean_squared_error, mean_absolute_error

# ============================
# 1. Load Excel data
# ============================
excel_path = "year_comparisons.xlsx"

df = pd.read_excel(excel_path, sheet_name="Rensad_lista")


# Quick sanity check
print("Columns:", df.columns.tolist())
print("Number of rows:", len(df))

# ============================
# 2. Helper functions
# ============================
def year_set(start, end):
    """
    Return a set of all years from start to end (inclusive).
    Assumes start and end are finite numbers.
    """
    start = int(start)
    end = int(end)
    return set(range(start, end + 1))

def interval_metrics(true_start, true_end, pred_start, pred_end):
    """
    Compute precision, recall, and F1 based on temporal set overlap:
      precision = |T ∩ P| / |P|
      recall    = |T ∩ P| / |T|
      F1        = 2 * |T ∩ P| / (|T| + |P|)
    If any of the intervals are missing/invalid, returns (0, 0, 0).
    """
    # Handle missing values (NaN)
    if pd.isna(true_start) or pd.isna(true_end) or pd.isna(pred_start) or pd.isna(pred_end):
        return 0.0, 0.0, 0.0

    T = year_set(true_start, true_end)
    P = year_set(pred_start, pred_end)

    if len(T) == 0 or len(P) == 0:
        return 0.0, 0.0, 0.0

    inter = T & P

    precision = len(inter) / len(P)
    recall = len(inter) / len(T)
    f1 = 2 * len(inter) / (len(T) + len(P))  # Sørensen–Dice

    return precision, recall, f1


# ============================
# 3. Compute metrics per model
# ============================

models = ["Claude", "Gpt", "Mistral", "Llama"]

# For each model, create three new columns in the dataframe:
# e.g. Claude_Precision, Claude_Recall, Claude_F1
for model in models:
    prec_vals = []
    rec_vals = []
    f1_vals = []

    for _, row in df.iterrows():
        p, r, f = interval_metrics(
            row["Libris_start"], row["Libris_end"],     # true interval
            row[f"{model}_Start"], row[f"{model}_End"]  # predicted interval
        )
        prec_vals.append(p)
        rec_vals.append(r)
        f1_vals.append(f)

    df[f"{model}_Precision"] = prec_vals
    df[f"{model}_Recall"] = rec_vals
    df[f"{model}_F1"] = f1_vals


# ============================
# 4. Print average metrics
# ============================

summary_rows = []
for model in models:
    p_mean = df[f"{model}_Precision"].mean()
    r_mean = df[f"{model}_Recall"].mean()
    f_mean = df[f"{model}_F1"].mean()

    summary_rows.append({
        "Model": model,
        "Precision_avg": p_mean,
        "Recall_avg": r_mean,
        "F1_avg": f_mean
    })

summary_df = pd.DataFrame(summary_rows)
print("\n=== Average interval metrics per model (Rensad_lista) ===")
print(summary_df.to_string(index=False))


# ============================
# 5. (Optional) Save results to a new Excel file
# ============================

output_path = "year_comparisons_with_metrics.xlsx"
df.to_excel(output_path, sheet_name="Rensad_lista_with_metrics", index=False)
print(f"\nSaved detailed metrics to: {output_path}")