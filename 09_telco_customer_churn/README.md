# Telco Customer Churn Prediction

## Business Problem
Telecom companies lose significant revenue when customers cancel their 
subscriptions. Identifying customers likely to churn in advance allows 
targeted retention efforts before they leave.

## Approach
- Cleaned and explored telecom customer data using Pandas
- Trained and compared classification models (Logistic Regression, Random Forest) to predict churn
- Evaluated models using appropriate classification metrics
- Built an interactive Streamlit dashboard to visualize churn drivers and predict churn risk for individual customers

## Tools & Libraries
Python, Streamlit, Scikit-learn, Pandas, Matplotlib, Seaborn, Joblib

## Key Insight
Certain contract types and tenure lengths were strong predictors of 
churn, allowing the business to prioritize retention offers for 
high-risk customer segments rather than applying blanket discounts.

## Files
- Streamlit app script
- Saved model file (Joblib)