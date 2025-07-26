import pandas as pd
from io import BytesIO

def generate_statistics_table(df_final):
    stats = df_final.groupby("ΤΜΗΜΑ").agg({
        "ΟΝΟΜΑ": "count",
        "ΦΥΛΟ": lambda x: (x == "Α").sum(),
        "ΖΩΗΡΟΣ": lambda x: (x == "Ν").sum(),
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": lambda x: (x == "Ν").sum(),
        "ΓΝΩΣΗ": lambda x: (x == "Ο").sum()
    }).rename(columns={
        "ΟΝΟΜΑ": "Σύνολο",
        "ΦΥΛΟ": "Αγόρια",
        "ΖΩΗΡΟΣ": "Ζωηροί",
        "ΙΔΙΑΙΤΕΡΟΤΗΤΑ": "Ιδιαιτερότητες",
        "ΓΝΩΣΗ": "Όχι Καλή Γνώση"
    })
    stats["Κορίτσια"] = stats["Σύνολο"] - stats["Αγόρια"]
    stats["Καλή Γνώση"] = stats["Σύνολο"] - stats["Όχι Καλή Γνώση"]
    stats.reset_index(inplace=True)
    return stats

def export_statistics_to_excel(stats_df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        stats_df.to_excel(writer, index=False, sheet_name='Στατιστικά')
    return output
