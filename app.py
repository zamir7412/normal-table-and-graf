import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

# הגדרות דף
st.set_page_config(page_title="מחשבון התפלגות נורמלית מתקדם", layout="wide")
st.title("מחשבון התפלגות נורמלית סטנדרטית $Z$")

# תפריט בחירה לסוג החישוב
mode = st.radio(
    "בחר את סוג החישוב:",
    ["שטח משמאל: $P(Z \leq z)$", "שטח מימין: $P(Z \geq z)$", "שטח בין ערכים: $P(z_1 \leq Z \leq z_2)$"],
    horizontal=True
)

# הגדרת ערכי z בהתאם לבחירה
if mode == "שטח בין ערכים: $P(z_1 \leq Z \leq z_2)$":
    col1, col2 = st.columns(2)
    with col1:
        z1 = st.number_input("הזן ערך $z_1$ (נמוך):", value=-1.0, step=0.01, format="%.2f")
    with col2:
        z2 = st.number_input("הזן ערך $z_2$ (גבוה):", value=1.0, step=0.01, format="%.2f")
    z_main = z2 # לצורך הצגת הטבלה
else:
    z_main = st.number_input("הזן ערך $z$:", value=1.25, step=0.01, format="%.2f")

# חישובים ורישום מתמטי
st.subheader("1. רישום וחישוב מתמטי")

if "משמאל" in mode:
    prob = norm.cdf(z_main)
    st.latex(rf"P(Z \leq {z_main:.2f}) = \Phi({z_main:.2f}) = {prob:.4f}")
elif "מימין" in mode:
    prob = 1 - norm.cdf(z_main)
    st.latex(rf"P(Z \geq {z_main:.2f}) = 1 - \Phi({z_main:.2f}) = 1 - {norm.cdf(z_main):.4f} = {prob:.4f}")
else:
    prob = norm.cdf(z2) - norm.cdf(z1)
    st.latex(rf"P({z1:.2f} \leq Z \leq {z2:.2f}) = \Phi({z2:.2f}) - \Phi({z1:.2f})")
    st.latex(rf"= {norm.cdf(z2):.4f} - {norm.cdf(z1):.4f} = {prob:.4f}")

percentage = prob * 100
st.write(f"**הסתברות:** {prob:.4f} | **אחוז מהשטח:** {percentage:.2f}%")

---

# 2. גרף עקומת ההתפלגות
st.subheader("2. עקומת התפלגות נורמלית")
fig, ax = plt.subplots(figsize=(10, 4))
x = np.linspace(-4, 4, 1000)
y = norm.pdf(x)
ax.plot(x, y, 'black', lw=2)

# הגדרת תחום צביעה לפי המצב
if "משמאל" in mode:
    x_fill = np.linspace(-4, z_main, 500)
    label_text = f"z = {z_main}"
elif "מימין" in mode:
    x_fill = np.linspace(z_main, 4, 500)
    label_text = f"z = {z_main}"
else:
    x_fill = np.linspace(z1, z2, 500)
    label_text = f"z1={z1}, z2={z2}"

y_fill = norm.pdf(x_fill)
ax.fill_between(x_fill, y_fill, color='skyblue', alpha=0.5)

# הוספת טקסט האחוז בתוך השטח
mean_fill = np.mean(x_fill)
ax.text(mean_fill, 0.05, f"{percentage:.1f}%", fontsize=12, fontweight='bold', ha='center')

ax.set_ylim(0, 0.45)
ax.set_title(f"Distribution Area: {mode.split(':')[0]}")
st.pyplot(fig)

---

# 3. טבלת התפלגות נורמלית (עבור הערך המרכזי)
st.subheader("3. איתור בטבלת ההתפלגות ($\Phi$)")
st.write(f"להלן הצגת הערך עבור $z = {z_main:.2f}$ בטבלה הסטנדרטית:")

# לוגיקה לבניית הטבלה והבלטה
row_val = np.floor(abs(z_main) * 10) / 10 * np.sign(z_main)
col_val = round(abs(z_main) - abs(row_val), 2)

rows = np.around(np.arange(row_val - 0.2, row_val + 0.3, 0.1), 1)
cols = np.around(np.arange(0.00, 0.10, 0.01), 2)
df = pd.DataFrame(index=rows, columns=[f"{c:.2f}" for c in cols])

for r in rows:
    for c in cols:
        df.loc[r, f"{c:.2f}"] = f"{norm.cdf(r + c if r>=0 else r-c):.4f}"

def highlight_cell(x):
    df_style = pd.DataFrame('', index=x.index, columns=x.columns)
    target_col = f"{col_val:.2f}"
    if row_val in x.index:
        df_style.loc[row_val, :] = 'background-color: #f0f0f0'
    if target_col in x.columns:
        df_style.loc[:, target_col] = 'background-color: #f0f0f0'
    if row_val in x.index and target_col in x.columns:
        df_style.loc[row_val, target_col] = 'background-color: #ffff00; color: black; font-weight: bold'
    return df_style

st.table(df.style.apply(highlight_cell, axis=None))