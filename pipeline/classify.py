import xgboost as xgb
import pandas as pd
import joblib
import os

# Once HDBSCAN identifies the clusters historically, we can't run it in real-time
# (it's too slow and needs the whole dataset).
# Instead, we train an XGBoost classifier to learn the HDBSCAN labels, which lets
# us classify a brand new wallet's feature vector in milliseconds.

def train_realtime_classifier(features_df, model_out="xgb_model.joblib"):
    print("Preparing data for XGBoost...")
    
    # Drop noise points (-1) and any wallets that weren't classified
    train_df = features_df[features_df['cluster'] >= 0].copy()
    if train_df.empty:
        print("Warning: No valid clusters to train on!")
        return None

    X = train_df.drop(columns=['wallet', 'cluster']).fillna(0)
    y = train_df['cluster']

    # Fairly standard hyperparams for a quick baseline
    clf = xgb.XGBClassifier(
        n_estimators=100, 
        max_depth=5, 
        learning_rate=0.1, 
        objective='multi:softprob',
        n_jobs=-1
    )
    
    print("Training XGBoost classifier...")
    clf.fit(X, y)
    
    out_path = os.path.join(os.path.dirname(__file__), "../data", model_out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(clf, out_path)
    
    print(f"Saved real-time classifier to {out_path}")
    return clf

if __name__ == "__main__":
    # TODO: Wire this up to read the actual output from cluster.py
    print("XGBoost module ready.")
