
import pandas as pd
import itertools
from collections import defaultdict
from penalty_score_step4 import calculate_penalty_score_step4

def get_fully_mutual_groups(df, class_col="ΤΜΗΜΑ"):
    """
    Εντοπισμός αδιαίρετων ομάδων 2 ή 3 μαθητών με πλήρως αμοιβαία φιλία.
    Αγνοεί σπασμένες φιλίες από προηγούμενα βήματα (δηλ. μαθητές με διαφορετικό class_col).
    """
    unplaced = df[df[class_col].isna()]
    used = set()
    groups = []

    for _, row in unplaced.iterrows():
        name = row["ΟΝΟΜΑ"]
        if name in used:
            continue
        friend = row["ΦΙΛΟΣ"]
        if pd.isna(friend) or friend in used or friend == name:
            continue
        friend_row = unplaced[unplaced["ΟΝΟΜΑ"] == friend]
        if friend_row.empty:
            continue
        if friend_row.iloc[0]["ΦΙΛΟΣ"] == name:
            # Πλήρως αμοιβαία δυάδα
            groups.append([name, friend])
            used.update([name, friend])

    # Προσπάθεια εύρεσης τριάδων
    final_groups = []
    for group in groups:
        a, b = group
        third_candidates = list(set(unplaced["ΟΝΟΜΑ"]) - set(group) - used)
        for c in third_candidates:
            c_row = unplaced[unplaced["ΟΝΟΜΑ"] == c]
            if c_row.empty:
                continue
            c_friend = c_row.iloc[0]["ΦΙΛΟΣ"]
            if c_friend in group and df[df["ΟΝΟΜΑ"] == c_friend]["ΦΙΛΟΣ"].values[0] == c:
                final_groups.append(group + [c])
                used.add(c)
                break
        else:
            final_groups.append(group)

    # Προσθήκη μεμονωμένων μη τοποθετημένων μαθητών που δεν είχαν πλήρως αμοιβαίες φιλίες
    for name in unplaced["ΟΝΟΜΑ"]:
        if name not in used:
            final_groups.append([name])
            used.add(name)

    return final_groups

def categorize_group(df, group):
    """
    Επιστρέφει την κατηγορία μιας ομάδας βάσει φύλου και γνώσης ελληνικών.
    """
    members = df[df["ΟΝΟΜΑ"].isin(group)]
    genders = members["ΦΥΛΟ"].unique()
    greek_levels = members["ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"].unique()

    if len(genders) > 1:
        return "Μικτού Φύλου"
    gender = genders[0]
    if len(greek_levels) == 1:
        if greek_levels[0] == "Ν":
            return f"Καλή Γνώση ({'Αγόρια' if gender == 'Α' else 'Κορίτσια'})"
        else:
            return f"Όχι Καλή Γνώση ({'Αγόρια' if gender == 'Α' else 'Κορίτσια'})"
    else:
        return f"Μικτής Γνώσης ({'Αγόρια' if gender == 'Α' else 'Κορίτσια'})"

def assign_groups(df, groups_by_category, num_classes):
    """
    Εκτελεί κατανομή όλων των ομάδων στα τμήματα και επιστρέφει το νέο df.
    """
    df_copy = df.copy()
    class_map = defaultdict(list)

    for category, group_list in groups_by_category.items():
        group_list = group_list.copy()
        group_list.sort(key=lambda g: -len(g))  # μεγαλύτερες ομάδες πρώτα

        # Καταμέτρηση υφιστάμενης κατάστασης
        counts = {f"Α{i+1}": 0 for i in range(num_classes)}
        for klass in class_map:
            counts[klass] += sum(1 for group in class_map[klass] if categorize_group(df, group) == category)

        i = 0
        for group in group_list:
            target_class = min(counts, key=counts.get)
            class_map[target_class].append(group)
            counts[target_class] += 1
            i += 1

    for klass, group_list in class_map.items():
        for group in group_list:
            for name in group:
                df_copy.loc[df_copy["ΟΝΟΜΑ"] == name, "ΤΜΗΜΑ"] = klass

    return df_copy

def step4_filikoi_omades(df, num_classes, scenario3_cols, scenario_prefix="ΒΗΜΑ4_ΣΕΝΑΡΙΟ_"):
    """
    Βήμα 4 – Ομαδοποίηση και κατανομή μαθητών βάσει πλήρως αμοιβαίας φιλίας και γνώσης ελληνικών.
    """
    results = []

    for idx, col in enumerate(scenario3_cols):
        df_copy = df.copy()
        df_copy["ΤΜΗΜΑ"] = df_copy[col]

        groups = get_fully_mutual_groups(df_copy)
        groups_by_cat = defaultdict(list)
        for group in groups:
            cat = categorize_group(df_copy, group)
            groups_by_cat[cat].append(group)

        distributed_df = assign_groups(df_copy, groups_by_cat, num_classes)
        score = calculate_penalty_score_step4(distributed_df)
        results.append((distributed_df.copy(), score))

    if not results:
        return df

    # Επιλογή σεναρίων με το μικρότερο score
    min_score = min(s for _, s in results)
    best = [r for r in results if r[1] == min_score]
    if len(best) > 5:
        best = best[:5]

    final = df.copy()
    for i, (scenario_df, _) in enumerate(best):
        final[f"{scenario_prefix}{i+1}"] = scenario_df["ΤΜΗΜΑ"]

    return final
