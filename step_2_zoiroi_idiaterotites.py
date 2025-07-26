import pandas as pd
import itertools
from helpers import (
    has_external_conflict,
    exceeds_imbalance,
    calculate_penalty_score,
    all_scenarios_have_conflicts,
    resolve_with_friendship
)

def step2_zoiroi_kai_idiaterotites(df, num_classes, senario1_col, scenario_prefix="ΒΗΜΑ2_ΣΕΝΑΡΙΟ_"):
    """
    Βήμα 2 – Συνδυαστική τοποθέτηση ζωηρών και μαθητών με ιδιαιτερότητες.
    df: αρχικό DataFrame
    num_classes: αριθμός διαθέσιμων τμημάτων
    senario1_col: στήλη ΒΗΜΑ1_ΣΕΝΑΡΙΟ_X (π.χ. ΒΗΜΑ1_ΣΕΝΑΡΙΟ_1)
    scenario_prefix: πρόθεμα για τη νέα στήλη (π.χ. ΒΗΜΑ2_ΣΕΝΑΡΙΟ_1)
    """
    df = df.copy()
    df["current_class"] = df[senario1_col]

    # Μαθητές που δεν έχουν τοποθετηθεί αλλά είναι ζωηροί ή/και με ιδιαιτερότητα
    movable_students = df[df["current_class"].isna() & ((df["ΖΩΗΡΟΣ"] == "Ν") | (df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"))]
    movable_names = movable_students["ΟΝΟΜΑ"].tolist()

    # 🔁 Early return: αν δεν υπάρχουν μαθητές προς κατανομή, αντιγράφουμε την τρέχουσα στήλη
    if len(movable_names) == 0:
        new_col_name = f"{scenario_prefix}{senario1_col[-1]}"
        df[new_col_name] = df["current_class"]
        return df

    # Όλοι οι δυνατοί συνδυασμοί ανάθεσης για τους movable
    all_combos = list(itertools.product(range(1, num_classes + 1), repeat=len(movable_names)))

    valid_scenarios = []
    scenario_scores = []

    for combo in all_combos:
        temp_df = df.copy()
        temp_df["temp_class"] = temp_df["current_class"]

        for i, name in enumerate(movable_names):
            temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "temp_class"] = f"Α{combo[i]}"

        if has_external_conflict(temp_df):
            continue

        if exceeds_imbalance(temp_df, "ΖΩΗΡΟΣ", num_classes, max_diff=1):
            continue

        if exceeds_imbalance(temp_df, "ΙΔΙΑΙΤΕΡΟΤΗΤΑ", num_classes, max_diff=1):
            continue

        score = calculate_penalty_score(temp_df)
        valid_scenarios.append(temp_df.copy())
        scenario_scores.append(score)

    if not valid_scenarios:
        print("⚠️ Δεν βρέθηκε έγκυρο σενάριο για Βήμα 2.")
        return df

    if all_scenarios_have_conflicts(valid_scenarios, movable_names):
        best_index = resolve_with_friendship(valid_scenarios, scenario_scores, movable_names)
    else:
        min_score = min(scenario_scores)
        best_indices = [i for i, s in enumerate(scenario_scores) if s == min_score]

        # Επιλογή με προτεραιότητα στη φιλία και στην ισορροπία φύλου, αν υπάρχουν πολλοί με ίδιο score
        if len(best_indices) > 1:
            best_index = resolve_with_friendship([valid_scenarios[i] for i in best_indices], [scenario_scores[i] for i in best_indices], movable_names)
        else:
            best_index = best_indices[0]

    # Δημιουργία νέας στήλης ΒΗΜΑ2_ΣΕΝΑΡΙΟ_X με την τελική τοποθέτηση
    new_col_name = f"{scenario_prefix}{senario1_col[-1]}"
    df[new_col_name] = df["current_class"]

    best_df = valid_scenarios[best_index]
    for _, row in best_df.iterrows():
        df.loc[df["ΟΝΟΜΑ"] == row["ΟΝΟΜΑ"], new_col_name] = row["temp_class"]

    return df
