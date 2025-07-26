
import pandas as pd
from helpers import calculate_penalty_score, resolve_with_friendship

def step3_amivaia_filia(df, num_classes, scenario2_cols, scenario_prefix="ΒΗΜΑ3_ΣΕΝΑΡΙΟ_"):
    """
    Βήμα 3 – Τοποθέτηση Μη Τοποθετημένων Μαθητών βάσει Πλήρους Αμοιβαίας Φιλίας
    Επιστρέφονται έως 5 σενάρια με το μικρότερο score και λιγότερες σπασμένες φιλίες.
    """
    scenario_results = []

    for i, scen_col in enumerate(scenario2_cols):
        temp_df = df.copy()
        temp_df["temp_class"] = temp_df[scen_col]

        unplaced = temp_df[temp_df["temp_class"].isna()]
        placed = temp_df[temp_df["temp_class"].notna()]

        for _, row in unplaced.iterrows():
            name = row["ΟΝΟΜΑ"]
            friend = row["ΦΙΛΟΣ"]
            if pd.notna(friend):
                friend_row = placed[placed["ΟΝΟΜΑ"] == friend]
                if not friend_row.empty and friend_row.iloc[0]["ΦΙΛΟΣ"] == name:
                    klass = friend_row.iloc[0]["temp_class"]
                    temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "temp_class"] = klass

        score = calculate_penalty_score(temp_df)
        scenario_results.append((temp_df.copy(), score))

    if not scenario_results:
        print("⚠️ Δεν υπάρχουν έγκυρα σενάρια στο Βήμα 3.")
        return df

    # Φιλτράρισμα μόνο αυτών με το μικρότερο score
    min_score = min(score for _, score in scenario_results)
    best_scenarios = [(df_, s) for df_, s in scenario_results if s == min_score]

    # Αν είναι πάνω από 5, προτεραιότητα σε λιγότερες σπασμένες φιλίες
    if len(best_scenarios) > 5:
        def count_broken_friendships(df_):
            broken = 0
            for _, row in df_.iterrows():
                name = row["ΟΝΟΜΑ"]
                friend = row["ΦΙΛΟΣ"]
                if pd.notna(friend):
                    friend_row = df_[df_["ΟΝΟΜΑ"] == friend]
                    if not friend_row.empty and friend_row.iloc[0]["ΦΙΛΟΣ"] == name:
                        if row["temp_class"] != friend_row.iloc[0]["temp_class"]:
                            broken += 1
            return broken

        best_scenarios.sort(key=lambda x: count_broken_friendships(x[0]))
        top_scenarios = best_scenarios[:5]
    else:
        top_scenarios = best_scenarios

    # Δημιουργία τελικού DataFrame με στήλες ΒΗΜΑ3_ΣΕΝΑΡΙΟ_1 έως 5
    df_result = df.copy()
    for idx, (scenario_df, _) in enumerate(top_scenarios):
        col_name = f"{scenario_prefix}{idx + 1}"
        df_result[col_name] = scenario_df["temp_class"]

    return df_result
