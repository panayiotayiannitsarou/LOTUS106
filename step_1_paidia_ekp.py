
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

        if len(set(combo)) == 1:
            continue

        counts = [len(v) for v in class_map.values()]
        if max(counts) - min(counts) > 1:
            continue

        if has_external_conflict(temp_df):
            continue

        normalized_signature = frozenset(tuple(sorted(group)) for group in class_map.values())
        if normalized_signature in seen_combinations:
            continue
        seen_combinations.add(normalized_signature)

        valid_scenarios.append(temp_df)

    def count_broken_friendships(df):
        broken = 0
        for name in names:
            row = df[df["ΟΝΟΜΑ"] == name]
            if row.empty:
                continue
            friends_raw = row.iloc[0].get("ΦΙΛΟΙ")
            if pd.isna(friends_raw):
                continue
            friends = [f.strip() for f in str(friends_raw).split(",") if f.strip()]
            for friend in friends:
                if friend in names and are_friends(df, name, friend):
                    if df.loc[df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"].values[0] != df.loc[df["ΟΝΟΜΑ"] == friend, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"].values[0]:
                        broken += 1
        return broken

    if len(valid_scenarios) > 5:
        valid_scenarios.sort(key=count_broken_friendships)
        min_broken = count_broken_friendships(valid_scenarios[0])
        valid_scenarios = [s for s in valid_scenarios if count_broken_friendships(s) == min_broken][:5]

    return valid_scenarios
