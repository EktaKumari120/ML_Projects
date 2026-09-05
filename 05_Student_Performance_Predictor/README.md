# Student Performance Predictor

## Business Problem
Predict a student's academic performance/score based on measurable 
factors (e.g., study habits, attendance, prior scores), so educators can 
identify students who may need additional support early.

## Approach
- Cleaned and explored student performance data using Pandas
- Trained a regression model with Scikit-learn to predict student scores
- Saved the trained model using Joblib for reuse without retraining
- Built a Streamlit app for users to input student details and get a predicted score

## Tools & Libraries
Python, Streamlit, Scikit-learn, Matplotlib, NumPy, Pandas, Joblib

## Key Insight
Key academic and behavioral factors could be combined into a single model 
to flag at-risk students before final results, enabling earlier intervention.

## Files
- Streamlit app script
- Saved model file (Joblib)