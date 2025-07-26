
import pandas as pd

def calculate_penalty_score_step4(df, class_col="ΤΜΗΜΑ"):
    """
    Υπολογισμός Penalty Score για το Βήμα 4 – Ισορροπία Φύλου και Γνώσης Ελληνικών.
    Ποινές:
    - Φύλο: +1 για κάθε μονάδα διαφοράς >2 ανά φύλο
    - Γλώσσα: +1 για κάθε μονάδα διαφοράς >3 ανά κατηγορία γνώσης (Ν/Ο)
    """
    score = 0
    df = df[df[class_col].notna()]  # αγνοούμε μη τοποθετημένους

    classes = df[class_col].unique()

    gender_counts = {}
    language_counts = {"Ν": {}, "Ο": {}}

    for klass in classes:
        group = df[df[class_col] == klass]
        boys = len(group[group["ΦΥΛΟ"] == "Α"])
        girls = len(group[group["ΦΥΛΟ"] == "Θ"])
        gender_counts[klass] = {"Α": boys, "Θ": girls}

        # Κατανομή Ν / Ο
        for code in ["Ν", "Ο"]:
            count = len(group[group["ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"] == code])
            language_counts[code][klass] = count

    # Ποινή Φύλου
    genders = list(gender_counts.values())
    for i in range(len(genders)):
        for j in range(i + 1, len(genders)):
            diff_boys = abs(genders[i]["Α"] - genders[j]["Α"])
            diff_girls = abs(genders[i]["Θ"] - genders[j]["Θ"])
            if diff_boys > 2:
                score += diff_boys - 2
            if diff_girls > 2:
                score += diff_girls - 2

    # Ποινή Γλώσσας
    for code in ["Ν", "Ο"]:
        values = list(language_counts[code].values())
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                diff = abs(values[i] - values[j])
                if diff > 3:
                    score += diff - 3

    return score
