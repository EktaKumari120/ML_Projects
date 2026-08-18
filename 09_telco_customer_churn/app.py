import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
plt.style.use('dark_background')
warnings.filterwarnings('ignore')

lr_model = joblib.load('lr_model.pkl')
rfc_model = joblib.load('rfc_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')

@st.cache_data
def load_data():
    return pd.read_csv('./data/telco_customer_churn.csv')

st.set_page_config(page_title='Customer Churn Prediction', page_icon='📉', layout='wide')

st.markdown("""
    <style>
    .main { background-color: #0f1117; }
    .stMetric { 
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #7c3aed;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0aec0;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #7c3aed;
        border-bottom: 3px solid #7c3aed;   
    }
    h1 { color: #7c3aed; }
    h2, h3 { color: #a78bfa; }
    </style>
""", unsafe_allow_html=True)

st.markdown("---")

st.title("Customer Churn Prediction")
st.markdown("Predict which telecom customers are likely to leave — and act before it is too late.")
tab1, tab2, tab3 = st.tabs([
    '📊 Data Explorer',
    '🤖 Model Comparison', 
    '🎯 Live Predictor'
])


with tab1:
    st.subheader("Customer Overview")
    
    # load the original dataframe here
    df = load_data()

    # three columns for metric cards
    col1, col2, col3 = st.columns(3)

    total = df.shape[0]
    churned = df[df['Churn'] == 'Yes'].shape[0]

    with col1:
        st.metric('Total Customers', total)
    with col2:
        st.metric('Churned Customers',churned)
    with col3:
        st.metric('Churn Rate', f"{(churned / total * 100):.1f}%")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig, ax = plt.subplots(figsize=(8,4))
        sns.countplot(x='Churn', data=df, ax=ax, palette=['#80ffdb', '#7400b8'])
        ax.set_title('Churn Distribution')
        ax.set_xlabel('Churn')
        ax.set_ylabel('Number of Customers')
        st.pyplot(fig)
        plt.close()
        
        
    with chart_col2:
        fig, ax = plt.subplots(figsize=(8,4))
        sns.boxplot(x='Churn', y='MonthlyCharges', data=df, ax= ax, palette=	['#80ffdb', '#7400b8'] )
        ax.set_title('Monthly Charges vs Churn')
        ax.set_xlabel('Churn')
        ax.set_ylabel('Monthly Charges ($)')
        st.pyplot(fig)
        plt.close()

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.countplot(x='Contract', hue='Churn', data=df, ax=ax, palette=['#80ffdb', '#7400b8'])
    ax.set_title('Contract Type vs Churn')
    ax.set_xlabel('Contract Type')
    ax.set_ylabel('Number of Customers')
    st.pyplot(fig)
    plt.close()

with tab2:
    st.subheader("Model Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Logistic Regression")
        st.metric("Accuracy", "81.97%")
        st.metric("ROC AUC", "86.04%")
        st.metric("Recall (Churners)", "58%")
    
    with col2:
        st.markdown("### Random Forest")
        st.metric("Accuracy", "79.41%")
        st.metric("ROC AUC", "83.00%")
        st.metric("Recall (Churners)", "46%")

    st.subheader("Feature Importance — What Drives Churn?")
    
    feature_importance = pd.DataFrame({
    'Feature': feature_names,
    'Importance': rfc_model.feature_importances_
    }).sort_values(by='Importance', ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x='Importance', y='Feature',
            data=feature_importance, palette=sns.color_palette('viridis', 15))
    ax.set_title('Top 15 Features Driving Customer Churn')
    ax.set_xlabel('Importance Score')
    ax.set_ylabel('Feature')
    st.pyplot(fig)
    plt.close()
    
with tab3:
    st.subheader("Predict Churn for a New Customer")
    
    # model selection
    model_choice = st.radio("Choose Model", 
                            ["Logistic Regression", "Random Forest"])
    
    st.markdown("### Enter Customer Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        monthly_charges = st.slider("Monthly Charges ($)", 18.0, 120.0, 65.0)
        
    with col2:
        contract = st.selectbox("Contract", 
                    ["Month-to-month", "One year", "Two year"])
        internet_service = st.selectbox("Internet Service",
                    ["DSL", "Fiber optic", "No"])
        tech_support = st.selectbox("Tech Support",
                    ["Yes","No","No internet service"])
        online_security = st.selectbox("Online Security",
                        ["Yes","No","No internet service"])
        payment_method = st.selectbox("Payment Method",
                                ["Electronic check","Mailed check","Bank transfer (automatic)","Credit card (automatic)"])
        online_backup = st.selectbox("Online Backup",
                ["Yes", "No", "No internet service"])
        device_protection = st.selectbox("Device Protection",
                ["Yes", "No", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV",
                ["Yes", "No", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies",
                ["Yes", "No", "No internet service"])
        multiple_lines = st.selectbox("Multiple Lines",
                ["Yes", "No", "No phone service"])
        gender = st.checkbox("Male")
        
    with col3:
        senior_citizen = st.checkbox("Senior Citizen")
        partner = st.checkbox("Has Partner")
        dependents = st.checkbox("Has Dependents")
        paperless_billing = st.checkbox("Paperless Billing")
        phone_service = st.checkbox("Phone Service")

    if st.button("🔍 Predict Churn", type="primary"):
        # Step 1 — start with all zeros for every feature
        input_data = {col: 0 for col in feature_names}

        # Step 2 — fill in numerical values directly
        input_data['tenure'] = tenure
        input_data['MonthlyCharges'] = monthly_charges
        input_data['SeniorCitizen'] = int(senior_citizen)
        input_data['Partner'] = int(partner)
        input_data['Dependents'] = int(dependents)
        input_data['PaperlessBilling'] = int(paperless_billing)
        input_data['PhoneService'] = int(phone_service)

        if contract == "One year":
            input_data['Contract_One year'] = 1
        elif contract == "Two year":
            input_data['Contract_Two year'] = 1
        # if Month-to-month — do nothing, already 0

        if internet_service == "Fiber optic":
            input_data['InternetService_Fiber optic'] = 1
        elif internet_service == "No":
            input_data['InternetService_No'] = 1

        if tech_support == "No internet service":
            input_data['TechSupport_No internet service'] = 1
        elif tech_support == "Yes":
            input_data['TechSupport_Yes'] = 1

        if online_security == "No internet service":
            input_data['OnlineSecurity_No internet service'] = 1
        elif online_security == "Yes":
            input_data['OnlineSecurity_Yes'] = 1

        if payment_method == "Credit card (automatic)":
            input_data['PaymentMethod_Credit card (automatic)'] = 1
        elif payment_method == "Electronic check":
            input_data['PaymentMethod_Electronic check'] = 1
        elif payment_method == "Mailed check":
            input_data['PaymentMethod_Mailed check'] = 1

        if online_backup == "No internet service":
            input_data['OnlineBackup_No internet service'] = 1
        elif online_backup == "Yes":
            input_data['OnlineBackup_Yes'] = 1

        if device_protection == "No internet service":
            input_data['DeviceProtection_No internet service'] = 1
        elif device_protection == "Yes":
            input_data['DeviceProtection_Yes'] = 1
        
        if streaming_tv == "No internet service":
            input_data['StreamingTV_No internet service'] = 1
        elif streaming_tv == "Yes":
            input_data['StreamingTV_Yes'] = 1

        if streaming_movies == "No internet service":
            input_data['StreamingMovies_No internet service'] = 1
        elif streaming_movies == "Yes":
            input_data['StreamingMovies_Yes'] = 1

        if multiple_lines == "No phone service":
            input_data['MultipleLines_No phone service'] = 1
        elif multiple_lines == "Yes":
            input_data['MultipleLines_Yes'] = 1

        input_data['gender'] = int(gender)

        # Step 3 — build dataframe and scale
        input_df = pd.DataFrame([input_data])
        input_scaled = scaler.transform(input_df)

        # Step 4 — select model and predict
        model = lr_model if model_choice == "Logistic Regression" else rfc_model
        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0][1]

        # Step 5 — show result (YOU WRITE THIS)
        if prediction == 1:
            st.error(f"⚠️ This customer is likely to churn — {probability*100:.1f}% probability")
        else:
            st.success(f"✅ This customer is likely to stay — {probability*100:.1f}% churn probability")
        if probability >= 0.3:
            st.warning("⚠️ Churn risk is elevated — consider a retention offer")
        st.metric("Churn Probability", f"{probability*100:.1f}%")
        
