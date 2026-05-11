import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

# הגדרות דף - מצב רחב לחיסכון במקום
st.set_page_config(page_title="מחשבון התפלגות נורמלית - קלמת", layout="wide")

# עיצוב כותרת קטנה יותר
st.markdown("<h2 style='text-align: center; color: #2E5A88;'>מחשבון התפלגות נורמלית סטנדרטית Z</h2>", unsafe_allow_html=True)

# חלוקה לעמודות: ימין לקלט וחישוב, שמאל לגרף וטבלה
col_input, col_viz = st.columns([1, 1.2])

with col_input:
    st.subheader("הגדרות וחישוב")
    mode = st.selectbox(
        "סוג החישוב:",
        ["שטח משמאל: P(Z ≤ z)", "שטח מימין: P(Z ≥ z)", "שטח בין ערכים: P(z1 ≤ Z ≤ z2)"]
    )

    if "בין ערכים" in mode:
        z1 = st.number_input("z1 (נמוך):", value=-1.0, step=0.01, format="%.2f")
        z2 = st.number_input("z2 (גבוה):", value=1.0, step=0.01, format="%.2f")
        z_main = z2
    else:
        z_main = st.number_input("הזן ערך z:", value=1.25, step=0.01, format="%.2f")

    # חישוב ורישום מתמטי
    if "משמאל" in mode:
        prob = norm.cdf(z_main)
        st.latex(rf"P(Z \leq {z_main:.2f}) = \Phi({z_main:.2f}) = {prob:.4f}")
    elif "מימין" in mode:
        prob = 1 - norm.cdf(z_main)
        st.latex(rf"P(Z \geq {z_main:.2f}) = 1 - \Phi({z_main:.2f}) = {prob:.4f}")
    else:
        prob = norm.cdf(z2) - norm.cdf(z1)
        st.latex(rf"P({z1:.2f} \leq Z \leq {z2:.2f}) = \Phi({z2:.2f}) - \Phi({z1:.2f}) = {prob:.4f}")

    st.info(f"**הסתברות:** {prob:.4f} | **אחוז:** {prob*100:.2f}%")

with col_viz:
    # 2. גרף קומפקטי ללא ציר Y
    fig, ax = plt.subplots(figsize=(7, 2.8)) # גודל מוקטן
    x = np.linspace(-4, 4, 1000)
    y = norm.pdf(x)
    ax.plot(x, y, 'black', lw=1.5)

    if "משמאל" in mode:
        x_fill = np.linspace(-4, z_main, 500)
    elif "מימין" in mode:
        x_fill = np.linspace(z_main, 4, 500)
    else:
        x_fill = np.linspace(z1, z2, 500)

    ax.fill_between(x_fill, norm.pdf(x_fill), color='#3498db', alpha=0.5)
    
    # הסרת שנתות ציר Y
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # הוספת אחוז בתוך הגרף
    ax.text(np.mean(x_fill), 0.02, f"{prob*100:.1f}%", ha='center', fontweight='bold', color='white')
    
    plt.tight_layout()
    st.pyplot(fig)

    # 3. טבלה ממוזערת
    st.write(f"איתור בטבלה עבור z={z_main:.2f}:")
    row_val = np.floor(round(z_main, 2) * 10) / 10
    col_val = round(z_main - row_val, 2)
    
    rows = np.around(np.arange(row_val - 0.1, row_val + 0.2, 0.1), 1)
    cols = np.around(np.arange(max(0, col_val - 0.02), min(0.09, col_val + 0.03), 0.01), 2)
    df = pd.DataFrame(index=rows, columns=[f"{c:.2f}" for c in cols])
    for r in rows:
        for c in cols: df.loc[r, f"{c:.2f}"] = f"{norm.cdf(r + c):.4f}"

    def highlight(x):
        style = pd.DataFrame('', index=x.index, columns=x.columns)
        if row_val in x.index and f"{col_val:.2f}" in x.columns:
            style.loc[row_val, f"{col_val:.2f}"] = 'background-color: yellow; font-weight: bold'
        return style

    st.table(df.style.apply(highlight, axis=None))
