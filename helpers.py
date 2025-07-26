
import pandas as pd

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

def exceeds_imbalance(df, column_name, num_classes, max_diff=1):
    counts = df[df[column_name] == "Ν"].groupby("temp_class").size()
    if counts.empty:
        return False
    return counts.max() - counts.min() > max_diff

def all_scenarios_have_conflicts(scenarios, names):
    for scenario_df in scenarios:
        score = calculate_penalty_score(scenario_df)
        if score == 0:
            return False
    return True

def resolve_with_friendship(scenario_dfs, scores, movable_names):
    min_broken_friendships = float("inf")
    best_index = 0

    for idx, df in enumerate(scenario_dfs):
        broken_friends = 0
        for name in movable_names:
            row = df[df["ΟΝΟΜΑ"] == name]
            if row.empty:
                continue
            friend = row.iloc[0]["ΦΙΛΟΣ"]
            if pd.isna(friend):
                continue
            friend_row = df[df["ΟΝΟΜΑ"] == friend]
            if friend_row.empty:
                continue
            if friend_row.iloc[0]["ΦΙΛΟΣ"] == name:
                if row.iloc[0]["temp_class"] != friend_row.iloc[0]["temp_class"]:
                    broken_friends += 1

        if broken_friends < min_broken_friendships:
            min_broken_friendships = broken_friends
            best_index = idx

    return best_index

def calculate_penalty_score(df):
    score = 0
    classes = df["temp_class"].dropna().unique()

    for class_name in classes:
        students_in_class = df[df["temp_class"] == class_name]
        for i, s1 in students_in_class.iterrows():
            for j, s2 in students_in_class.iterrows():
                if i >= j:
                    continue
                if s1["ΖΩΗΡΟΣ"] == "Ν" and s2["ΖΩΗΡΟΣ"] == "Ν":
                    score += 3
                elif (s1["ΖΩΗΡΟΣ"] == "Ν" and s2["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν") or                      (s1["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν" and s2["ΖΩΗΡΟΣ"] == "Ν"):
                    score += 4
                elif s1["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν" and s2["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν":
                    score += 5

    for i, row in df.iterrows():
        friend_name = row["ΦΙΛΟΣ"]
        if pd.notna(friend_name):
            friend_row = df[df["ΟΝΟΜΑ"] == friend_name]
            if not friend_row.empty and friend_row.iloc[0]["ΦΙΛΟΣ"] == row["ΟΝΟΜΑ"]:
                class1 = row["temp_class"]
                class2 = friend_row.iloc[0]["temp_class"]
                if class1 != class2:
                    if any([
                        row["ΖΩΗΡΟΣ"] == "Ν",
                        row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν",
                        row["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"
                    ]) and any([
                        friend_row.iloc[0]["ΖΩΗΡΟΣ"] == "Ν",
                        friend_row.iloc[0]["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν",
                        friend_row.iloc[0]["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"
                    ]):
                        score += 5

    gender_counts = {}
    for class_name in classes:
        group = df[df["temp_class"] == class_name]
        boys = len(group[group["ΦΥΛΟ"] == "Α"])
        girls = len(group[group["ΦΥΛΟ"] == "Θ"])
        gender_counts[class_name] = {"Α": boys, "Θ": girls}

    genders = list(gender_counts.values())
    for i in range(len(genders)):
        for j in range(i + 1, len(genders)):
            diff_boys = abs(genders[i]["Α"] - genders[j]["Α"])
            diff_girls = abs(genders[i]["Θ"] - genders[j]["Θ"])
            if diff_boys > 2:
                score += diff_boys - 2
            if diff_girls > 2:
                score += diff_girls - 2

    return score
