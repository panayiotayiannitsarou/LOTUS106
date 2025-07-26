
import pandas as pd
import itertools

def are_friends(df, name1, name2):
    row1 = df[df["ΟΝΟΜΑ"] == name1]
    row2 = df[df["ΟΝΟΜΑ"] == name2]
    if row1.empty or row2.empty:
        return False

    friends1 = row1.iloc[0].get("ΦΙΛΟΙ")
    friends2 = row2.iloc[0].get("ΦΙΛΟΙ")

    if pd.isna(friends1) or pd.isna(friends2):
        return False

    list1 = [f.strip() for f in str(friends1).split(",") if f.strip()]
    list2 = [f.strip() for f in str(friends2).split(",") if f.strip()]

    return name2 in list1 and name1 in list2

def has_external_conflict(df):
    for _, row in df.iterrows():
        conflicts = row["ΣΥΓΚΡΟΥΣΗ"]
        if pd.notna(conflicts):
            for other_name in conflicts.split(","):
                other_name = other_name.strip()
                if not other_name:
                    continue
                same_class = df.loc[df["ΟΝΟΜΑ"] == other_name, "temp_class"]
                if not same_class.empty and same_class.values[0] == row["temp_class"]:
                    return True
    return False

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

        temp_df["temp_class"] = temp_df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        if has_external_conflict(temp_df):
            continue

        signature = frozenset((k, tuple(sorted(v))) for k, v in class_map.items())
        if signature in seen_combinations:
            continue
        seen_combinations.add(signature)

        valid_scenarios.append(temp_df)

    def count_broken_friendships(df):
        if "ΦΙΛΟΙ" not in df.columns:
            return 0
        broken = 0
        for name in names:
            row = df[df["ΟΝΟΜΑ"] == name]
            if row.empty:
                continue
            friends_str = row.iloc[0]["ΦΙΛΟΙ"]
            if pd.isna(friends_str):
                continue
            friends = [f.strip() for f in friends_str.split(",") if f.strip()]
            for friend in friends:
                if friend in names and not are_friends(df, name, friend):
                    broken += 1
        return broken

    if len(valid_scenarios) > 5:
        valid_scenarios.sort(key=count_broken_friendships)
        min_broken = count_broken_friendships(valid_scenarios[0])
        valid_scenarios = [s for s in valid_scenarios if count_broken_friendships(s) == min_broken][:5]

    return valid_scenarios
