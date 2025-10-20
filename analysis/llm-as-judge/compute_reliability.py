import argparse
import glob
import json
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def safe_import_pingouin():
    try:
        import pingouin as pg  
        return pg
    except Exception as exc:  
        raise RuntimeError(
            "pingouin is required. Install with: pip install pingouin"
        ) from exc


def safe_import_sklearn():
    try:
        from sklearn.metrics import cohen_kappa_score 
        return cohen_kappa_score
    except Exception as exc:
        raise RuntimeError(
            "scikit-learn is required. Install with: pip install scikit-learn"
        ) from exc


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(name: str) -> str:
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        s = s.replace(" ", "_").replace("-", "_")
        return s.lower()

    mapping = {c: norm(c) for c in df.columns}
    return df.rename(columns=mapping)


COL_MAP: Dict[str, List[str]] = {
    "app_name": ["app_name", "app", "appname"],
    "model": ["model", "test_model"],
    "test_name": ["test_name", "test", "testname"],
    "evaluator": ["evaluator", "evaluation_model", "evaluator_model"],
    "overall_score": ["overall_score", "overall", "overall score"],
    "scenario_code_alignment_score": ["scenario_code_alignment_score", "scenario_code_alignment"],
    "code_structure_score": ["code_structure_score", "code_structure"],
    "selector_quality_score": ["selector_quality_score", "selector_quality"],
    "best_practices_score": ["best_practices_score", "best_practices"],
}


def pick_col(df: pd.DataFrame, aliases: List[str]) -> Optional[str]:
    for a in aliases:
        key = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", a).replace(" ", "_").lower()
        if key in df.columns:
            return key
    return None


def dataset_from_path(path: str) -> str:
    parts = path.split(os.sep)
    for p in parts:
        if p.endswith("-Evaluation"):
            return p.split("-Evaluation")[0]
    return "unknown"


def load_and_standardize(path: str) -> pd.DataFrame:
    raw = pd.read_csv(path)
    df = normalize_columns(raw)

    std = pd.DataFrame()
    std["dataset"] = dataset_from_path(path)

    for std_name, aliases in COL_MAP.items():
        col = pick_col(df, aliases)
        if col is not None:
            std[std_name] = df[col]

    for req in ["model", "test_name", "evaluator"]:
        if req not in std.columns:
            raise ValueError(f"Missing required column '{req}' in {path}")

    if "is_well_aligned" in std.columns:
        std["is_well_aligned"] = std["is_well_aligned"].map(
            lambda x: True
            if str(x).strip().lower() in {"true", "1", "yes"}
            else False
            if str(x).strip().lower() in {"false", "0", "no"}
            else np.nan
        )

    for m in [
        "overall_score",
        "scenario_code_alignment_score",
        "code_structure_score",
        "selector_quality_score",
        "best_practices_score",
    ]:
        if m in std.columns:
            std[m] = pd.to_numeric(std[m], errors="coerce")

    if "app_name" in std.columns:
        app_series = std["app_name"].astype(str)
    else:
        app_series = pd.Series([""] * len(std))
    std["unit_id"] = (
        app_series
        + "::"
        + std["model"].astype(str)
        + "::"
        + std["test_name"].astype(str)
    )
    std["source_file"] = path
    return std


def collect_frames(root: str, patterns: Optional[List[str]] = None, dataset: Optional[str] = None) -> pd.DataFrame:
    if not patterns:
        if dataset:
            patterns = [
                os.path.join(root, f"{dataset}-Evaluation", "*evaluation_results*.csv"),
                os.path.join(root, "**", f"{dataset}-Evaluation", "*evaluation_results*.csv"),
            ]
        else:
            patterns = [os.path.join(root, "**", "*evaluation_results*.csv")]
    files: List[str] = []
    for pat in patterns:
        files.extend(glob.glob(pat, recursive=True))
    frames: List[pd.DataFrame] = []
    for f in files:
        try:
            frames.append(load_and_standardize(f))
        except Exception as e:
            print(f"Skip {f}: {e}")
    if not frames:
        raise FileNotFoundError("No evaluation_results CSV files found.")
    return pd.concat(frames, ignore_index=True)


def keep_units_with_two_raters(df: pd.DataFrame) -> pd.DataFrame:
    counts = df.groupby("unit_id")["evaluator"].nunique()
    keep = counts[counts >= 2].index
    return df[df["unit_id"].isin(keep)].copy()


def compute_icc(df: pd.DataFrame, metric: str) -> Optional[Dict[str, float]]:
    if metric not in df.columns:
        return None
    sub = df[["unit_id", "evaluator", metric]].dropna()
    valid_units = sub.groupby("unit_id")["evaluator"].nunique()
    sub = sub[sub["unit_id"].isin(valid_units[valid_units >= 2].index)]
    if sub.empty:
        return None
    pg = safe_import_pingouin()
    icc_tbl = pg.intraclass_corr(data=sub, targets="unit_id", raters="evaluator", ratings=metric)
    out: Dict[str, Dict[str, float]] = {}
    res: Dict[str, float] = {}
    
    row2 = icc_tbl[icc_tbl["Type"] == "ICC2"].iloc[0]
    res["icc2"] = float(row2["ICC"])
    res["icc2_ci_low"] = float(row2["CI95%"][0])
    res["icc2_ci_high"] = float(row2["CI95%"][1])
    res["icc2_pval"] = float(row2["pval"])
    
    row3 = icc_tbl[icc_tbl["Type"] == "ICC3"].iloc[0]
    res["icc3"] = float(row3["ICC"])
    res["icc3_ci_low"] = float(row3["CI95%"][0])
    res["icc3_ci_high"] = float(row3["CI95%"][1])
    res["icc3_pval"] = float(row3["pval"])
    res["n_units"] = float(sub["unit_id"].nunique())
    return res


def compute_corr_and_bias(df: pd.DataFrame, metric: str) -> Optional[Dict[str, float]]:
    sub = df[["unit_id", "evaluator", metric]].dropna()
    wide = sub.pivot_table(index="unit_id", columns="evaluator", values=metric)
    wide = wide.dropna()
    if wide.shape[1] != 2 or wide.empty:
        return None
    cols = list(wide.columns)
    a, b = cols[0], cols[1]
    r = np.corrcoef(wide[a], wide[b])[0, 1]
    ans: Dict[str, float] = {
        "pearson_r": float(r),
        "n_pairs": float(len(wide)),
        f"mean_{a}": float(wide[a].mean()),
        f"mean_{b}": float(wide[b].mean()),
        f"sd_{a}": float(wide[a].std(ddof=1)),
        f"sd_{b}": float(wide[b].std(ddof=1)),
        f"mean_diff_{b}-{a}": float((wide[b] - wide[a]).mean()),
    }
    return ans


def compute_icc_after_z_by_rater(df: pd.DataFrame, metric: str) -> Optional[Dict[str, float]]:
    if metric not in df.columns:
        return None
    pg = safe_import_pingouin()
    zn = df.copy()
    def zfun(s: pd.Series) -> pd.Series:
        sd = s.std(ddof=1)
        if sd and sd > 0:
            return (s - s.mean()) / sd
        return pd.Series(np.zeros(len(s)), index=s.index)
    zn[f"{metric}_z"] = zn.groupby("evaluator")[metric].transform(zfun)
    sub = zn[["unit_id", "evaluator", f"{metric}_z"]].dropna()
    valid_units = sub.groupby("unit_id")["evaluator"].nunique()
    sub = sub[sub["unit_id"].isin(valid_units[valid_units >= 2].index)]
    if sub.empty:
        return None
    icc_tbl = pg.intraclass_corr(data=sub, targets="unit_id", raters="evaluator", ratings=f"{metric}_z")
    row2 = icc_tbl[icc_tbl["Type"] == "ICC2"].iloc[0]
    return {
        "icc2_z": float(row2["ICC"]),
        "icc2_z_ci_low": float(row2["CI95%"][0]),
        "icc2_z_ci_high": float(row2["CI95%"][1]),
        "icc2_z_pval": float(row2["pval"]),
    }



def main():
    parser = argparse.ArgumentParser(description="Compute inter-rater reliability metrics (ICC, kappa, etc.)")
    parser.add_argument("--root", default=os.getcwd(), help="Root directory to search evaluation CSVs")
    parser.add_argument("--dataset", default=None, help="Filter by dataset name (e.g., SauceDemo). If omitted, uses all.")
    parser.add_argument("--metric", default="overall_score", help="Numeric metric to use for ICC (default: overall_score)")
    parser.add_argument("--file", default=None, help="Optional single CSV file to load directly (bypasses search)")
    parser.add_argument("--json_out", default=None, help="Optional path to write JSON results")
    args = parser.parse_args()

    if args.file:
        df = load_and_standardize(args.file)
    else:
        df = collect_frames(args.root, dataset=args.dataset)
    if args.dataset:
        df = df[df["dataset"].astype(str).str.lower() == args.dataset.lower()]
        if df.empty:
            raise SystemExit(f"No data left after filtering dataset='{args.dataset}'.")
    df = keep_units_with_two_raters(df)

    results: Dict[str, Dict[str, float]] = {}

    icc_res = compute_icc(df, args.metric)
    if icc_res:
        results.update(icc_res)

    corr_bias = compute_corr_and_bias(df, args.metric)
    if corr_bias:
        results.update(corr_bias)

    icc_z = compute_icc_after_z_by_rater(df, args.metric)
    if icc_z:
        results.update(icc_z)

    print("=== Inter-rater reliability ===")
    if args.dataset:
        print(f"Dataset: {args.dataset}")
    print(f"Metric: {args.metric}")
    for k, v in results.items():
        print(f"{k}: {v}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved JSON to: {args.json_out}")


if __name__ == "__main__":
    main()


