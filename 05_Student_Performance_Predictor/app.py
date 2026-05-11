import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

# ── Load the saved model and scaler ─────────────────────────────────────
model  = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="centered"
)

# ── Header ───────────────────────────────────────────────────────────────
st.title("🎓 Student Score Predictor")
st.markdown("Fill in the student details below to predict their final exam score.")
st.divider()

# ── Input section ────────────────────────────────────────────────────────
st.subheader("Student Details")

col1, col2 = st.columns(2)

with col1:
    study_hours    = st.slider("Study hours per day",
                               min_value=1.0, max_value=10.0,
                               value=5.0, step=0.5)

    attendance     = st.slider("Attendance (%)",
                               min_value=50.0, max_value=100.0,
                               value=75.0, step=1.0)

    previous_score = st.slider("Previous exam score",
                               min_value=30.0, max_value=100.0,
                               value=65.0, step=1.0)

with col2:
    sleep_hours    = st.slider("Sleep hours per night",
                               min_value=4.0, max_value=9.0,
                               value=7.0, step=0.5)

    motivation     = st.slider("Motivation level (1–10)",
                               min_value=1, max_value=10,
                               value=6, step=1)

st.divider()

# ── Predict button ───────────────────────────────────────────────────────
if st.button('Predict Score', use_container_width=True,type='primary'):
    # Step 1: Collect inputs into the same format the model was trained on
    input_data = pd.DataFrame({
        'study_hours'    : [study_hours],
        'attendance'     : [attendance],
        'previous_score' : [previous_score],
        'sleep_hours'    : [sleep_hours],
        'motivation'     : [motivation]
    })
    # Step 2: Scale the input using the SAME scaler from training
    input_scaled = scaler.transform(input_data)

    # Step 3: Predict
    predicted_score = model.predict(input_scaled)[0]
    # Clip just in case the prediction goes slightly out of range
    predicted_score = np.clip(predicted_score, 0, 100)

    # ── Show the result ──────────────────────────────────────────────────
    st.subheader("Prediction Result")
    
    # Colour-code the score
    if predicted_score >= 75:
        st.success(f"Predicted Final Score: **{predicted_score:.1f} / 100**")
    elif predicted_score >= 50:
        st.warning(f"Predicted Final Score: **{predicted_score:.1f} / 100**")
    else:
        st.error(f"Predicted Final Score: **{predicted_score:.1f} / 100**")

    # ── Feature importance bar chart ─────────────────────────────────────
    st.subheader("What influenced this prediction?")

    feature_names = ['Study hours', 'Attendance', 'Previous score',
                     'Sleep hours', 'Motivation']
    coefficients  = model.coef_

    # Multiply coefficient by actual scaled input value
    contributions = np.abs(coefficients * input_scaled[0])
    
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ['steelblue' if c >= 0 else 'tomato' for c in coefficients]
    bars = ax.barh(feature_names, contributions, color=colors)
    ax.set_xlabel("Contribution to predicted score")
    ax.set_title("Feature contributions for this student")
    ax.bar_label(bars, fmt='%.2f', padding=4)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # ── Student summary ──────────────────────────────────────────────────
    st.subheader("Student Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)
    summary_col1.metric("Study hours",    f"{study_hours}h/day")
    summary_col2.metric("Attendance",     f"{attendance}%")
    summary_col3.metric("Previous score", f"{previous_score}/100")

    summary_col4, summary_col5 = st.columns(2)
    summary_col4.metric("Sleep",       f"{sleep_hours}h/night")
    summary_col5.metric("Motivation",  f"{motivation}/10")