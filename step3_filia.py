
import pandas as pd
from helpers import calculate_penalty_score, resolve_with_friendship

def step3_amivaia_filia(df, num_classes, scenario2_cols, scenario_prefix="ΒΗΜΑ3_ΣΕΝΑΡΙΟ_"):
    """
    Βήμα 3 – Τοποθέτηση Μη Τοποθετημένων Μαθητών βάσει Πλήρους Αμοιβαίας Φιλίας
    """
    final_results = []  # Λίστα με όλα τα DataFrames Βήματος 3
    scores = []         # Αντίστοιχα penalty scores

    for i, scen_col in enumerate(scenario2_cols):
        temp_df = df.copy()
        temp_df["temp_class"] = temp_df[scen_col]

        # Εύρεση μη τοποθετημένων
        unplaced = temp_df[temp_df["temp_class"].isna()]
        placed = temp_df[temp_df["temp_class"].notna()]

        # Για κάθε μη τοποθετημένο μαθητή
        for _, row in unplaced.iterrows():
            name = row["ΟΝΟΜΑ"]
            friend = row["ΦΙΛΟΣ"]

            # Αν υπάρχει φίλος και είναι πλήρως αμοιβαία η σχέση
            if pd.notna(friend):
                friend_row = placed[placed["ΟΝΟΜΑ"] == friend]
                if not friend_row.empty and friend_row.iloc[0]["ΦΙΛΟΣ"] == name:
                    # Τοποθέτηση στο ίδιο τμήμα με τον φίλο
                    klass = friend_row.iloc[0]["temp_class"]
                    temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "temp_class"] = klass

        # Υπολογισμός score για το σενάριο
        score = calculate_penalty_score(temp_df)
        scores.append(score)
        final_results.append(temp_df.copy())

    # Επιλογή σεναρίου με το μικρότερο score
    min_score = min(scores)
    best_indices = [i for i, s in enumerate(scores) if s == min_score]

    if len(best_indices) > 1:
        best_index = resolve_with_friendship([final_results[i] for i in best_indices],
                                             [scores[i] for i in best_indices],
                                             temp_df[temp_df["temp_class"].isna()]["ΟΝΟΜΑ"].tolist())
    else:
        best_index = best_index = best_indices[0]

    # Προσθήκη νέων στηλών ΒΗΜΑ3_ΣΕΝΑΡΙΟ_X
    df_result = df.copy()
    for idx, temp_df in enumerate(final_results):
        col_name = f"{scenario_prefix}{idx + 1}"
        df_result[col_name] = temp_df["temp_class"]

    return df_result
