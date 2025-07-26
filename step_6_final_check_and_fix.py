# step6_final_check_and_fix.py

import pandas as pd
import random
from collections import Counter
from copy import deepcopy

def step6_final_check_and_fix(df, num_classes, senario_col):
    df = df.copy()
    df['ΤΜΗΜΑ'] = df[senario_col]

    # ➤ Κατηγοριοποίηση Μαθητών σε Κατηγορίες
    def categorize(row):
        gender = row['ΦΥΛΟ']
        knowledge = row['ΓΝΩΣΗ']
        if pd.isna(gender) or pd.isna(knowledge):
            return None
        if gender == 'Μικτό':
            return 'Μικτό'
        if knowledge == 'Ν':
            return f'Καλή Γνώση ({"Αγόρια" if gender == "Α" else "Κορίτσια"})'
        elif knowledge == 'Ο':
            return f'Όχι Καλή Γνώση ({"Αγόρια" if gender == "Α" else "Κορίτσια"})'
        elif knowledge == 'Ν+Ο':
            return f'Μικτής Γνώσης ({"Αγόρια" if gender == "Α" else "Κορίτσια"})'
        return None

    df['ΚΑΤΗΓΟΡΙΑ'] = df.apply(categorize, axis=1)

    # ➤ Συγκέντρωση Ομάδων προς Ανταλλαγή (από Βήματα 4–5 μόνο)
    movable = df[df['ΠΡΟΕΛΕΥΣΗ'].isin(['ΒΗΜΑ4', 'ΒΗΜΑ5'])].copy()

    def count_by_col(data, col):
        counts = {cls: Counter(data[data['ΤΜΗΜΑ'] == cls][col]) for cls in range(1, num_classes + 1)}
        return counts

    gender_counts = count_by_col(df, 'ΦΥΛΟ')
    knowledge_counts = count_by_col(df, 'ΓΝΩΣΗ')

    # ➤ Εύρεση Απόκλισης
    def get_diff(counts, key):
        vals = [counts[c].get(key, 0) for c in counts]
        return max(vals) - min(vals)

    gender_diff = get_diff(gender_counts, 'Α')  # Αγόρια
    knowledge_diff = get_diff(knowledge_counts, 'Ν')  # Καλή γνώση

    # ➤ Ανταλλαγές για Ισορροπία
    df_best = df.copy()
    best_score = 9999

    for _ in range(30):  # Πολλαπλές προσπάθειες
        df_temp = df.copy()

        # Επανατοποθέτηση κινητών μαθητών τυχαία στα ίδια τμήματα
        for i, row in movable.iterrows():
            df_temp.at[i, 'ΤΜΗΜΑ'] = random.randint(1, num_classes)

        gender_counts = count_by_col(df_temp, 'ΦΥΛΟ')
        knowledge_counts = count_by_col(df_temp, 'ΓΝΩΣΗ')

        gender_pen = sum(max(0, abs(gender_counts[c]['Α'] - gender_counts[c2]['Α']) - 3)
                         for c in gender_counts for c2 in gender_counts if c != c2) * 2
        knowledge_pen = sum(max(0, abs(knowledge_counts[c]['Ν'] - knowledge_counts[c2]['Ν']) - 3)
                            for c in knowledge_counts for c2 in knowledge_counts if c != c2) * 3

        score = gender_pen + knowledge_pen

        # ➤ Αν είναι καλύτερο, κρατάμε
        if score < best_score:
            best_score = score
            df_best = df_temp.copy()

    df_result = df.copy()
    df_result['ΤΜΗΜΑ'] = df_best['ΤΜΗΜΑ']
    return df_result, best_score
