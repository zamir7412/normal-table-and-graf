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
col_input, col_viz = st.columns([1, 1.3])

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
    fig, ax = plt.subplots(figsize=(7, 2.5)) 
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
    
    # הסרת שנתות ציר Y ושיפור המראה
    ax.set_yticks([])
    ax.set_yticklabels([])
    for side in ['left', 'top', 'right']:
        ax.spines[side].set_visible(False)
    
    # הוספת אחוז בתוך הגרף
    ax.text(np.mean(x_fill), 0.02, f"{prob*100:.1f}%", ha='center', fontweight='bold', color='black')
    
    plt.tight_layout()
    st.pyplot(fig)

    # 3. טבלה ממוזערת עם כותרות נקיות (כמו בתמונה)
    st.write(f"איתור בטבלה עבור z={z_main:.2f}:")
    
    # הכנת נתוני הטבלה
    row_val = np.floor(round(z_main, 2) * 10) / 10
    col_val = round(z_main - row_val, 2)
    
    rows = np.around(np.arange(row_val - 0.1, row_val + 0.2, 0.1), 1)
    cols = np.around(np.arange(0.00, 0.10, 0.01), 2)
    
    # יצירת שמות כותרות נקיים (למשל .05 במקום 0.05)
    clean_col_names = [f"{c:.2f}".replace("0.", ".") for c in cols]
    clean_row_names = [f"{r:.1f}" for r in rows]
    
    df = pd.DataFrame(index=clean_row_names, columns=clean_col_names)
    
    for r in rows:
        for c in cols:
            df.loc[f"{r:.1f}", f"{c:.2f}".replace("0.", ".")] = f"{norm.cdf(r + c if r>=0 else r-c):.4f}"

    def highlight(data):
        style = pd.DataFrame('', index=data.index, columns=data.columns)
        target_row = f"{row_val:.1f}"
        target_col = f"{col_val:.2f}".replace("0.", ".")
        
        if target_row in data.index and target_col in data.columns:
            style.loc[target_row, target_col] = 'background-color: #ffff00; color: black; font-weight: bold; border: 1.5px solid black'
        return style

    st.table(df.style.apply(highlight, axis=None))
