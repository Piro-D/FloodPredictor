import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from preprocess import fit_preprocess

# ================================================
# LOAD DATA
# ================================================
df = pd.read_csv("data/flood_training_data_kelurahan_use.csv")

# Normalize kelurahan early
df["subdistrict_name"] = (
    df["subdistrict_name"]
    .str.lower()
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)




# ================================================
# SEPARATE FEATURES & LABEL
# ================================================
target_column = "flood"
y = df[target_column]
X_raw = df.drop(columns=[target_column])




# ================================================
# PREPROCESS
# ================================================
X = fit_preprocess(X_raw)

print("Sample processed features:")
print(X.head())





# ================================================
# TRAIN / TEST SPLIT
# ================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)




# ================================================
# TRAIN MODEL
# ================================================
model = XGBClassifier(
    n_estimators=250,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.9,
    colsample_bytree=0.9,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

# Get feature names AFTER preprocessing
feature_names = X.columns.tolist()



# ================================================
# Importance testing
# ================================================

# importance = model.get_booster().get_score(importance_type="gain")
# importance_df = pd.DataFrame({
#     "feature": feature_names,
#     "gain": [importance.get(f, 0.0) for f in feature_names]
# })

# importance_df = importance_df.sort_values("gain", ascending=False)

# print("\n===== FEATURE IMPORTANCE (GAIN) =====")
# print(importance_df)



# ================================================
# EVALUATION
# ================================================
y_pred = model.predict(X_test)

print("\n===== MODEL PERFORMANCE =====")
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred))



# ================================================
# SAVE MODEL
# ================================================
joblib.dump(model, "models/flood_xgb_model.pkl")
print("Model saved.")
