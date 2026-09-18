# Credit Card Fraud Detection (Ensembles + Imbalanced Classification)

## Business Problem
A bank wants to automatically flag potentially fraudulent credit card 
transactions in real time. Missing real fraud costs money directly; 
flagging too many legitimate transactions as fraud increases customer 
friction and manual review workload.

## Approach
- Worked with a real, extremely imbalanced dataset (284,807 
  transactions, only 0.17% fraud)
- Demonstrated concretely why accuracy is a misleading metric here — 
  a 99.91% accurate baseline model still missed 41% of real fraud
- Compared class weighting vs SMOTE across Logistic Regression, 
  Random Forest, XGBoost, and LightGBM; found moderate class weighting 
  consistently outperformed extreme correction settings
- Combined class weighting with decision threshold tuning for a 
  further-improved trade-off between recall and false alarms
- Built a weighted Voting Ensemble (Random Forest + XGBoost + 
  LightGBM), achieving the best F1-score (0.86) across every tested 
  configuration
- Validated the final model's learned patterns against independent 
  EDA correlation findings, confirming genuine signal over noise
- Investigated a $0-transaction fraud pattern (8x higher fraud rate 
  than average) as an additional, deployable business insight
- Saved the final production model with joblib

## Tools & Libraries
Python, Scikit-learn, XGBoost, LightGBM, imbalanced-learn (SMOTE), 
Pandas, NumPy, Matplotlib, Seaborn, joblib

## Key Insight
A model can appear highly "accurate" while completely failing at its 
actual business purpose on rare-event problems. Proper evaluation 
(Precision, Recall, F1, ROC-AUC, Precision-Recall curves) and careful, 
moderate imbalance correction — not maximal correction — produced the 
best real-world result: catching 77% of fraud with only 2 false 
alarms per ~56,700 transactions.

## Files
- `notebook.ipynb` — full analysis, code, and visualizations
- `data/creditcard.csv` — **not included in this repo due to GitHub's 
  100MB file size limit.** Download it directly from Kaggle: 
  [Credit Card Fraud Detection Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) 
  and place it in the `data/` folder to run the notebook.
- `outputs/` — saved charts and the final trained model (.pkl)