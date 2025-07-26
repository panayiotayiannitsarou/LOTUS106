
import pandas as pd
import random
from collections import Counter
from copy import deepcopy

def step5_xwris_filies(df, num_classes, senario_col):
    df = deepcopy(df)
    class_cols = [f"ΒΗΜΑ5_ΣΕΝΑΡΙΟ_{i+1}" for i in range(5)]
    all_results = []

    for scenario_index in range(5):
        col_name = f"ΒΗΜΑ4_ΣΕΝΑΡΙΟ_{scenario_index+1}"
        if col_name not in df.columns:
            continue
        df_working = df.copy()
        df_working["TMP_ΤΜΗΜΑ"] = df_working[col_name]

        # Εντοπισμός μη τοποθετημένων
        unplaced = df_working[df_working["TMP_ΤΜΗΜΑ"].isna()].copy()
        placed = df_working[~df_working["TMP_ΤΜΗΜΑ"].isna()].copy()

        # Στατιστικά ανά τμήμα
        def get_class_stats(d):
            counts = d["TMP_ΤΜΗΜΑ"].value_counts().to_dict()
            genders = d.groupby("TMP_ΤΜΗΜΑ")["ΦΥΛΟ"].value_counts().unstack().fillna(0).to_dict("index")
            return counts, genders

        for idx, row in unplaced.iterrows():
            counts, genders = get_class_stats(placed)

            # Βρες τα τμήματα με τους λιγότερους μαθητές
            min_count = min(counts.values()) if counts else 0
            candidate_classes = [i for i in range(1, num_classes+1) if counts.get(i, 0) == min_count]

            # Αν ισοπαλία => κριτήριο ισορροπίας φύλου
            if len(candidate_classes) > 1:
                diffs = {}
                for cls in candidate_classes:
                    boys = genders.get(cls, {}).get("Α", 0)
                    girls = genders.get(cls, {}).get("Θ", 0)
                    future = boys + girls + 1
                    if row["ΦΥΛΟ"] == "Α":
                        boys += 1
                    else:
                        girls += 1
                    diffs[cls] = abs(boys - girls)

                best_class = min(diffs, key=diffs.get)
            else:
                best_class = candidate_classes[0]

            df_working.at[idx, "TMP_ΤΜΗΜΑ"] = best_class
            placed = pd.concat([placed, df_working.loc[[idx]]])

        df[f"ΒΗΜΑ5_ΣΕΝΑΡΙΟ_{scenario_index+1}"] = df_working["TMP_ΤΜΗΜΑ"]

    return df
