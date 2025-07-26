import streamlit as st
import pandas as pd
import math
from io import BytesIO

from statistics import generate_statistics_table, export_statistics_to_excel
from step_1_paidia_ekp import generate_teacher_kids_scenarios

# --- Αρχικοποίηση session state ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "df_final" not in st.session_state:
    st.session_state.df_final = None

# --- Κωδικός Πρόσβασης ---
PASSWORD = "1234"
if not st.session_state.authenticated:
    pwd = st.text_input("🔐 Εισάγετε Κωδικό Πρόσβασης:", type="password")
    if pwd == PASSWORD:
        st.session_state.authenticated = True
        st.experimental_rerun()
    else:
        st.stop()

# --- Όροι Χρήσης ---
with st.expander("📜 Όροι Χρήσης & Πνευματικά Δικαιώματα"):
    st.markdown("""
    Αυτή η εφαρμογή αποτελεί πνευματική ιδιοκτησία του δημιουργού.\
    Απαγορεύεται η αναπαραγωγή, διανομή ή τροποποίηση χωρίς άδεια.
    """)

# --- Τίτλος ---
st.title("🎓 Ψηφιακή Κατανομή Μαθητών Α' Δημοτικού")

# --- Επανεκκίνηση ---
if st.button("🔄 Επανεκκίνηση Εφαρμογής"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()

# --- Ενεργοποίηση/Απενεργοποίηση Εφαρμογής ---
active = st.toggle("🟢 Ενεργοποίηση Εφαρμογής", value=True)
if not active:
    st.warning("Η εφαρμογή είναι ανενεργή.")
    st.stop()

# --- Ανέβασμα Excel ---
uploaded_file = st.file_uploader("📥 Ανέβασε Excel Αρχείο Μαθητών", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    total_students = len(df)
    num_classes = math.ceil(total_students / 25)

    st.success(f"✅ Το αρχείο ανέβηκε! Μαθητές: {total_students} → Τμήματα: {num_classes}")

    # --- Εκτέλεση Κατανομής ---
    if st.button("⚙️ Εκτέλεση Κατανομής Μαθητών"):
        with st.spinner("🔄 Εκτελείται κατανομή σεναρίων Βήμα 1 έως 6..."):
            from steps.step_2_zoiroi_idiaterotites import step2_zoiroi_kai_idiaterotites
            from steps.step3_filia import step3_amivaia_filia
            from steps.step4_filikoi_omades import step4_filikoi_omades
            from steps.step5_xwris_filies import step5_xwris_filies
            from steps.step6_final_check_and_fix import step6_final_check_and_fix

            best_df = None
            best_score = float("inf")

            step1_scenarios = generate_teacher_kids_scenarios(df, num_classes)

            for idx1, df1 in enumerate(step1_scenarios):
                senario1_col = f"ΒΗΜΑ1_ΣΕΝΑΡΙΟ_{idx1+1}"
                df1[senario1_col] = df1["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]

                df2 = step2_zoiroi_kai_idiaterotites(df1, num_classes, senario1_col)
                scenario2_cols = [col for col in df2.columns if col.startswith("ΒΗΜΑ2_ΣΕΝΑΡΙΟ_")]
                df3 = step3_amivaia_filia(df2, num_classes, scenario2_cols)

                scenario3_cols = [col for col in df3.columns if col.startswith("ΒΗΜΑ3_ΣΕΝΑΡΙΟ_")]
                df4 = step4_filikoi_omades(df3, num_classes, scenario3_cols)

                df5 = step5_xwris_filies(df4, num_classes, scenario3_cols)

                for i in range(1, 6):
                    col = f"ΒΗΜΑ5_ΣΕΝΑΡΙΟ_{i}"
                    if col not in df5.columns:
                        continue
                    df6, score = step6_final_check_and_fix(df5, num_classes, col)
                    if score < best_score:
                        best_score = score
                        best_df = df6.copy()

            if best_df is not None:
                st.session_state.df_final = best_df
                st.success("✅ Ολοκληρώθηκε η κατανομή και επιλέχθηκε το καλύτερο σενάριο.")
            else:
                st.error("⚠️ Δεν βρέθηκε έγκυρο σενάριο κατανομής.")

if st.session_state.df_final is not None:
    st.subheader("📈 Στατιστικά Τελικής Κατανομής")

    stats_df = generate_statistics_table(st.session_state.df_final)
    st.dataframe(stats_df)

    output_stats = export_statistics_to_excel(stats_df)
    st.download_button(
        label="📥 Κατέβασμα Excel – Στατιστικά Τελικής Κατανομής",
        data=output_stats.getvalue(),
        file_name="statistika_telikis_katanomis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Πίνακας Ονομάτων ανά Τμήμα ---
    st.subheader("🧾 Ονόματα Μαθητών ανά Τμήμα")
    df_final = st.session_state.df_final
    class_columns = sorted(df_final["ΤΜΗΜΑ"].dropna().unique())
    for tmima in class_columns:
        with st.expander(f"Τμήμα {tmima}"):
            st.dataframe(df_final[df_final["ΤΜΗΜΑ"] == tmima][["ΟΝΟΜΑ"]].reset_index(drop=True))

    output_final = BytesIO()
    with pd.ExcelWriter(output_final, engine='xlsxwriter') as writer:
        st.session_state.df_final.to_excel(writer, index=False, sheet_name='Τελικό')

    st.download_button(
        label="📤 Κατέβασμα Excel – Τελική Κατανομή",
        data=output_final.getvalue(),
        file_name="kalytero_senario.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Λογότυπο κάτω δεξιά ---
from PIL import Image

logo_path = "assets/logo.png"
try:
    logo = Image.open(logo_path)
    st.markdown(
        """
        <style>
        .custom-logo-container {
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 9999;
        }
        </style>
        <div class="custom-logo-container">
        """,
        unsafe_allow_html=True
    )
    st.image(logo, width=100)
    st.markdown("</div>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

with st.sidebar:
    st.markdown("""
    <div style='position:fixed; bottom:10px; right:10px;'>
        <img src='https://via.placeholder.com/100x40?text=Logo' style='width:100px;'>
    </div>
    """, unsafe_allow_html=True)
