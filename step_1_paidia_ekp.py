import pandas as pd
import itertools
from helpers import (
    has_external_conflict,
    are_friends,
)

def generate_teacher_kids_scenarios(df, num_classes):
    df = df.copy()
    teacher_kids = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"]
    names = teacher_kids["ΟΝΟΜΑ"].tolist()

    if len(names) == 0:
        return [df]

    # Αν τα παιδιά είναι λιγότερα ή ίσα από τα τμήματα
    if len(names) <= num_classes:
        df_copy = df.copy()
        for i, name in enumerate(names):
            df_copy.loc[df_copy["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = f"Α{i+1}"
        return [df_copy]

    all_combos = list(itertools.product(range(1, num_classes + 1), repeat=len(names)))
    valid_scenarios = []
    seen_combinations = set()

    for combo in all_combos:
        temp_df = df.copy()
        class_map = {}
        for i, name in enumerate(names):
            klass = f"Α{combo[i]}"
            class_map.setdefault(klass, []).append(name)
            temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = klass

        # Απόρριψη αν όλα στο ίδιο τμήμα
        if len(set(combo)) == 1:
            continue

        # Απόρριψη αν διαφορά >1
        counts = [len(v) for v in class_map.values()]
        if max(counts) - min(counts) > 1:
            continue

        # Απόρριψη αν έχει εξωτερική σύγκρουση
        if has_external_conflict(temp_df):
            continue

        # Κανονικοποίηση – αποφυγή διπλών σεναρίων
        signature = frozenset((k, tuple(sorted(v))) for k, v in class_map.items())
        if signature in seen_combinations:
            continue
        seen_combinations.add(signature)

        valid_scenarios.append(temp_df)

    # Φιλτράρισμα με βάση σπασμένες φιλίες
    def count_broken_friendships(df):
        broken = 0
        for name in names:
            friend = df.loc[df["ΟΝΟΜΑ"] == name, "ΦΙΛΟΣ"].values[0]
            if friend in names:
                if not are_friends(df, name, friend):
                    broken += 1
        return broken

    if len(valid_scenarios) > 5:
        valid_scenarios.sort(key=count_broken_friendships)
        min_broken = count_broken_friendships(valid_scenarios[0])
        valid_scenarios = [s for s in valid_scenarios if count_broken_friendships(s) == min_broken][:5]

    return valid_scenarios
