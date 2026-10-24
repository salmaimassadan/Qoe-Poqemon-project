"""Turn the notebook's result CSVs into LaTeX tables for the report.

Run from the repository root after executing the notebook:
    python report/make_tables.py
"""
import ast
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "report" / "tables"
OUT.mkdir(exist_ok=True)

FEATURE_SET_LABELS = {"objective": "Objective (no QoF)", "with_feedback": "With feedback (QoF)"}
MODEL_ORDER = ["Dummy", "kNN", "SVC", "Decision tree", "XGBoost"]


def mean_std(m, s):
    return f"{m:.3f} $\\pm$ {s:.3f}"


def results_table():
    cv = pd.read_csv(RESULTS / "cv_summary.csv")
    test = pd.read_csv(RESULTS / "test_summary.csv")
    df = cv.merge(test, on=["feature_set", "model"])
    lines = [
        r"\begin{tabular}{llccc|ccc}",
        r"\toprule",
        r" & & \multicolumn{3}{c|}{5-fold grouped CV (training users)} & \multicolumn{3}{c}{Held-out test users} \\",
        r"Features & Model & Macro-F1 & Accuracy & MAE & Macro-F1 & Accuracy & MAE \\",
        r"\midrule",
    ]
    for fs, label in FEATURE_SET_LABELS.items():
        sub = df[df.feature_set == fs].set_index("model").loc[MODEL_ORDER]
        for i, (model, r) in enumerate(sub.iterrows()):
            name = f"\\textbf{{{model}}}$^\\star$" if r.selected_by_cv else model
            first = f"\\multirow{{{len(sub)}}}{{*}}{{{label}}}" if i == 0 else ""
            lines.append(
                f"{first} & {name} & {mean_std(r.cv_f1_macro, r.cv_f1_macro_std)} & "
                f"{mean_std(r.cv_accuracy, r.cv_accuracy_std)} & {mean_std(r.cv_mae, r.cv_mae_std)} & "
                f"{r.test_f1_macro:.3f} & {r.test_accuracy:.3f} & {r.test_mae:.3f} \\\\"
            )
        lines.append(r"\midrule" if fs != list(FEATURE_SET_LABELS)[-1] else r"\bottomrule")
    lines.append(r"\end{tabular}")
    (OUT / "results.tex").write_text("\n".join(lines) + "\n")


def best_params_table():
    cv = pd.read_csv(RESULTS / "cv_summary.csv")
    lines = [r"\begin{tabular}{lp{0.4\linewidth}p{0.4\linewidth}}", r"\toprule",
             r"Model & Objective (no QoF) & With feedback (QoF) \\", r"\midrule"]
    for model in MODEL_ORDER[1:]:
        cells = []
        for fs in FEATURE_SET_LABELS:
            params = ast.literal_eval(cv[(cv.model == model) & (cv.feature_set == fs)].best_params.iloc[0])
            cells.append(", ".join(f"\\texttt{{{k.replace('_', chr(92) + '_')}}}={v}" for k, v in params.items()))
        lines.append(f"{model} & {cells[0]} & {cells[1]} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "best_params.tex").write_text("\n".join(lines) + "\n")


def split_effect_table():
    se = pd.read_csv(RESULTS / "split_effect.csv")
    lines = [r"\begin{tabular}{llcc}", r"\toprule",
             r"Features & CV folds & Macro-F1 & Accuracy \\", r"\midrule"]
    for fs, label in FEATURE_SET_LABELS.items():
        for split in ["random", "grouped"]:
            r = se[(se.feature_set == fs) & (se.split == split)].iloc[0]
            lines.append(f"{label if split == 'random' else ''} & {split} & "
                         f"{mean_std(r.f1_macro, r.f1_macro_std)} & {mean_std(r.accuracy, r.accuracy_std)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "split_effect.tex").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    results_table()
    best_params_table()
    split_effect_table()
    print(f"Tables written to {OUT}")
