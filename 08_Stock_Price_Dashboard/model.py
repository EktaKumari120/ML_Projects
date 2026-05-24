import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from data import fetch_stock_data

'''
MA_7, MA_21          → What's the trend direction?
RSI                  → Is it overbought/oversold?
Bollinger Bands      → Is price at an extreme?
MACD                 → Is momentum accelerating?
Previous_Close       → What was yesterday's price?
Daily_Return         → What's the recent % move?
Volume_Ratio         → Is this move backed by real activity?
Price_to_MA          → How far from normal is the price?
'''

def add_features(df):
    df = df.copy()

    # Moving averages — average of last N days' closing price
    df["MA_7"] = df["Close"].rolling(window=7).mean()   # 7-day moving avg
    df["MA_21"] = df["Close"].rolling(window=21).mean() # 21-day moving avg

    # RSI - Relative Strength Index (momentum indicator)
    # Measures if stock is overbought (>70) or oversold (<30)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands (volatility indicator)
    # Shows price range with upper and lower bounds
    rolling_mean = df["Close"].rolling(window=20).mean()
    rolling_std = df["Close"].rolling(window=20).std()
    df["BB_upper"] = rolling_mean + (rolling_std * 2)
    df["BB_lower"] = rolling_mean - (rolling_std * 2)
    df["BB_width"] = df["BB_upper"] - df["BB_lower"]
    
    # MACD - Moving Average Convergence Divergence
    # Shows trend changes
    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp1 - exp2
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    
    # Lag features 
    df["Previous_Close"] = df["Close"].shift(1)
    df["Prev_2_Close"] = df["Close"].shift(2)  # 2 days ago

    # Returns
    df["Daily_Return"] = df["Close"].pct_change()
    df["Return_7d"] = df["Close"].pct_change(periods=7)  # weekly return
    
    # Volume features
    df["Volume_MA_7"] = df["Volume"].rolling(window=7).mean()
    df["Volume_Ratio"] = df["Volume"] / df["Volume_MA_7"]
    
    # Price position relative to moving averages
    df["Price_to_MA7"] = df["Close"] / df["MA_7"]
    df["Price_to_MA21"] = df["Close"] / df["MA_21"]
    
    # Drop rows with NaN
    df.dropna(inplace=True)
    
    return df


def train_all_models(df):
    features = [
    "MA_7", "MA_21",
    "RSI",
    "BB_upper", "BB_lower", "BB_width",
    "MACD", "MACD_signal",
    "Previous_Close", "Prev_2_Close",
    "Daily_Return", "Return_7d",
    "Volume_MA_7", "Volume_Ratio",
    "Price_to_MA7", "Price_to_MA21"
    ]
    target = "Close"
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # define all 4 models
    models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=42
    ),
    "XGBoost": XGBRegressor(
        n_estimators=200,
        max_depth=7,
        learning_rate=0.05,
        random_state=42,
        verbosity=0
    ),
    "SVR": SVR(
        kernel="rbf",
        C=1000,
        gamma="scale",
        epsilon=0.01
    )
} 

    results = {}
    trained_models = {}
    all_predictions = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        results[name] = round(mae, 4)
        trained_models[name] = model
        all_predictions[name] = preds
    
    return trained_models, results, all_predictions, X_test, y_test


def smart_ensemble_predict(trained_models, results, df):
    """
    Intelligent ensemble that only combines models within 2x of best MAE.
    If only one model qualifies, uses it directly instead of averaging.
    """
    features = [
        "MA_7", "MA_21",
        "RSI",
        "BB_upper", "BB_lower", "BB_width",
        "MACD", "MACD_signal",
        "Previous_Close", "Prev_2_Close",
        "Daily_Return", "Return_7d",
        "Volume_MA_7", "Volume_Ratio",
        "Price_to_MA7", "Price_to_MA21"
    ]
    
    last_row = df[features].iloc[[-1]]
    
    # Find best model
    best_mae = min(results.values())
    threshold = best_mae * 2
    
    # Only use models within threshold
    good_models = {name: model for name, model in trained_models.items() 
                   if results[name] <= threshold}
    
    predictions_dict = {}
    
    if len(good_models) == 1:
        # Only one good model, use it directly
        model_name = list(good_models.keys())[0]
        prediction = list(good_models.values())[0].predict(last_row)[0]
        predictions_dict[model_name] = prediction
        return round(float(prediction), 2), predictions_dict, "Best Model Only"
    
    else:
        # Multiple good models, do weighted ensemble
        predictions = []
        weights = []
        
        for name, model in good_models.items():
            pred = model.predict(last_row)[0]
            predictions_dict[name] = pred
            mae = results[name]
            weight = 1 / (mae + 0.01)
            predictions.append(pred)
            weights.append(weight)
        
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        weighted_pred = sum(p * w for p, w in zip(predictions, weights))
        
        return round(float(weighted_pred), 2), predictions_dict, "Weighted Ensemble"


#### --------Test------------
# from data import fetch_stock_data

# df = fetch_stock_data("AAPL", "1y")
# df = add_features(df)

# trained_models, results, all_predictions, X_test, y_test = train_all_models(df)
# ensemble_result, individual_preds, method = smart_ensemble_predict(trained_models, results, df)
# print("Model MAEs:")
# for name, mae in results.items():
#     print(f"  {name}: ${mae:.2f}")

# print(f"\nPrediction Method: {method}")
# print(f"Final Prediction: ${ensemble_result}")
# print(f"\nModels used:")
# for name, pred in individual_preds.items():
#     print(f"  {name}: ${pred:.2f}")