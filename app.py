import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

st.set_page_config(page_title="מחשבון התפלגות נורמלית - קלמת", layout="wide")

st.markdown("<h2 style='text-align: center; color: #2E5A88;'>מחשבון התפלגות נורמלית (X) וציוני תקן (Z)</h2>", unsafe_allow_html=True)

# תפריט לבחירת הנעלם
col_choice = st.columns([1, 2, 1])
with col_choice[1]:
    calc_mode = st.selectbox(
        "מה ברצונך לחשב?",
        ["הסתברות/שטח (P)", "ערך (x)", "ממוצע (μ)", "סטיית תקן (σ)"]
    )

st.divider()

col_input, col_viz = st.columns([1, 1.3])

with col_input:
    st.subheader("הזנת נתונים")
    
    # לוגיקה להצגת שדות קלט לפי הנעלם שנבחר
    x = mu = sigma = p_input = None

    if calc_mode == "הסתברות/שטח (P)":
        x = st.number_input("ערך (x):", value=110.0, step=0.1)
        mu = st.number_input("ממוצע (μ):", value=100.0, step=0.1)
        sigma = st.number_input("סטיית תקן (σ):", value=15.0, step=0.1, min_value=0.01)
        
        z = (x - mu) / sigma
        p_res = norm.cdf(z)
        
    elif calc_mode == "ערך (x)":
        p_input = st.number_input("הסתברות/שטח (0-1 או אחוז):", value=0.8413, step=0.01)
        if p_input > 1: p_input /= 100 # המרה מאחוז לשבר
        mu = st.number_input("ממוצע (μ):", value=100.0, step=0.1)
        sigma = st.number_input("סטיית תקן (σ):", value=15.0, step=0.1, min_value=0.01)
        
        z = norm.ppf(p_input)
        x = mu + z * sigma
        p_res = p_input

    elif calc_mode == "ממוצע (μ)":
        x = st.number_input("ערך (x):", value=110.0, step=0.1)
        p_input = st.number_input("הסתברות/שטח (0-1 או אחוז):", value=0.75, step=0.01)
        if p_input > 1: p_input /= 100
        sigma = st.number_input("סטיית תקן (σ):", value=15.0, step=0.1, min_value=0.01)
        
        z = norm.ppf(p_input)
        mu = x - z * sigma
        p_res = p_input

    elif calc_mode == "סטיית תקן (σ)":
        x = st.number_input("ערך (x):", value=110.0, step=0.1)
        mu = st.number_input("ממוצע (μ):", value=100.0, step=0.1)
        p_input = st.number_input("הסתברות/שטח (0-1 או אחוז):", value=0.75, step=0.01)
        if p_input > 1: p_input /= 100
        
        z = norm.ppf(p_input)
        if abs(z) < 0.001: 
            st.error("לא ניתן לחשב סטיית תקן כשהשטח הוא 0.5 (z=0)")
            sigma = 1
        else:
            sigma = (x - mu) / z
        p_res = p_input

    # הצגת התוצאה והדרך המתמטית
    st.subheader("תוצאה ודרך פתרון")
    st.latex(rf"z = \frac{{x - \mu}}{{\sigma}} = \frac{{{x:.2f} - {mu:.2f}}}{{{sigma:.2f}}} = {z:.2f}")
    st.latex(rf"P(X \leq {x:.2f}) = \Phi({z:.2f}) = {p_res:.4f}")
    
    st.success(f"הערך המחושב: **{ (p_res if calc_mode=='הסתברות/שטח (P)' else (x if calc_mode=='ערך (x)' else (mu if calc_mode=='ממוצע (μ)' else sigma))):.4f}**")

with col_viz:
    # גרף עם ציר X ריאלי
    fig, ax = plt.subplots(figsize=(7, 3))
    
    # טווח הגרף נקבע לפי הממוצע וסטיית התקן (3 סטיות תקן לכל צד)
    x_axis = np.linspace(mu - 3.5*sigma, mu + 3.5*sigma, 1000)
    y_axis = norm.pdf(x_axis, mu, sigma)
    ax.plot(x_axis, y_axis, 'black', lw=1.5)

    # צביעת השטח עד X
    x_fill = np.linspace(mu - 3.5*sigma, x, 500)
    ax.fill_between(x_fill, norm.pdf(x_fill, mu, sigma), color='#3498db', alpha=0.5)
    
    # עיצוב הגרף
    ax.set_yticks([])
    for side in ['left', 'top', 'right']: ax.spines[side].set_visible(False)
    ax.set_xlabel("ערכי X")
    
    # הוספת קו אנכי ב-X
    ax.axvline(x, color='red', linestyle='--', alpha=0.3)
    ax.text(x, ax.get_ylim()[1]*0.1, f"x={x:.1f}", ha='center', color='red', fontsize=10)
    
    st.pyplot(fig)

    # טבלת Z (תמיד מראה את ה-Z המתאים בטבלה הסטנדרטית)
    st.write(f"איתור z={z:.2f} בטבלת ההתפלגות:")
    row_val = np.floor(round(z, 2) * 10) / 10
    col_val = round(z - row_val, 2)
    
    rows = np.around(np.arange(row_val - 0.1, row_val + 0.2, 0.1), 1)
    cols = np.around(np.arange(0.00, 0.10, 0.01), 2)
    df = pd.DataFrame(index=[f"{r:.1f}" for r in rows], columns=[f"{c:.2f}".replace("0.", ".") for c in cols])
    
    for r in rows:
        for c in cols:
            df.loc[f"{r:.1f}", f"{c:.2f}".replace("0.", ".")] = f"{norm.cdf(r + c):.4f}"

    def highlight(data):
        style = pd.DataFrame('', index=data.index, columns=data.columns)
        r_str, c_str = f"{row_val:.1f}", f"{col_val:.2f}".replace("0.", ".")
        if r_str in data.index and c_str in data.columns:
            style.loc[r_str, c_str] = 'background-color: yellow; font-weight: bold; color: black'
        return style

    st.table(df.style.apply(highlight, axis=None))
