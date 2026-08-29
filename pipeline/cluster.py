import pandas as pd
import hdbscan
import joblib
from sklearn.preprocessing import StandardScaler

def train_clusters(features_df, output_model_path="xgb_cluster_model.joblib"):
    """
    Takes the aggregated wallet features, scales them, and runs HDBSCAN
    to find behavioral archetypes.
    """
    print("Preparing data for clustering...")
    
    # drop wallet address for the math part
    X = features_df.drop(columns=['wallet']).fillna(0)
    
    # Scale features (HDBSCAN relies heavily on distance metrics)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("Running HDBSCAN... this might take a minute on large datasets.")
    # min_cluster_size is a magic number we need to tune
    clusterer = hdbscan.HDBSCAN(min_cluster_size=500, min_samples=50, metric='euclidean')
    labels = clusterer.fit_predict(X_scaled)
    
    features_df['cluster'] = labels
    
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"Found {num_clusters} clusters!")
    
    # Normally we would train an XGBoost classifier here to learn the HDBSCAN labels
    # so we can predict in real-time on the stream without rerunning HDBSCAN.
    # TODO: Add XGBoost step
    
    return features_df, clusterer

if __name__ == "__main__":
    pass
