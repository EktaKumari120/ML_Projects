import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt

# ── Step 1: Load data ───────────────────────────────────────────────────
df = pd.read_csv('student_data.csv')

# Separate features (inputs) from target
X = df.drop('final_score', axis=1)   
y = df['final_score'] 

print("Features shape:", X.shape)
print("Target shape:", y.shape)
print("\nFeature columns:", list(X.columns))

# ── Step 2: Split into train and test sets ──────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      
    random_state=42     
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")

# ── Step 3: Scale the features ──────────────────────────────────────────
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print("\nBefore scaling — study_hours mean:", X_train['study_hours'].mean().round(2))
print("After scaling  — study_hours mean:", X_train_scaled[:, 0].mean().round(4))

# ── Step 4: Train the model ─────────────────────────────────────────────
model = LinearRegression()
model.fit(X_train_scaled, y_train)

print("\nModel trained successfully!")

# ── Step 5: Predictions on the test set ────────────────────────────
y_pred = model.predict(X_test_scaled)

# ── Step 6: Evaluate the model ──────────────────────────────────────────
mae  = mean_absolute_error(y_test, y_pred)
mse  = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print("\n── Model Performance ──")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R²   : {r2:.4f}")

# ── Step 7: Visualise actual vs predicted ───────────────────────────────
plt.figure(figsize=(7,5))
plt.scatter(y_test, y_pred, alpha=0.4, color='teal', s=20)
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         color='red', linewidth=1.5, linestyle='--')
plt.xlabel('Actual score')
plt.ylabel('Predicted score')
plt.title('Actual vs Predicted scores')
plt.tight_layout()
plt.savefig('plot_actual_vs_predicted.png')
plt.show()

# ── Step 8: Feature importance (coefficients) ───────────────────────────
feature_names = list(X.columns)
coefficients  = model.coef_

coef_df = pd.DataFrame({
    'feature': feature_names,
    'coefficient': coefficients
}).sort_values('coefficient', ascending=False)

print("\n── Feature Importance (coefficients) ──")
print(coef_df)

plt.figure(figsize=(7, 4))
plt.barh(coef_df['feature'], coef_df['coefficient'], color='steelblue')
plt.xlabel('Coefficient value')
plt.title('How much each feature influences the final score')
plt.tight_layout()
plt.savefig('plot_feature_importance.png')
plt.show()

# ── Step 9: Save the model and scaler ───────────────────────────────────
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')

print("\nModel and scaler saved!")