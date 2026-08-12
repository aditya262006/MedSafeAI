"""
Train Neural Network model on drug feature dataset.
Run: python model/train.py
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.neural_network import MLPClassifier

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

FEATURE_COLS = [
    "side_effect_count",
    "severity_score",
    "serious_event_rate",
    "interaction_count",
    "interaction_flag",
    "has_high_interaction"
]

RISK_LABELS = ["Low", "Medium", "High"]

def load_data():
    """Load processed drug features CSV."""
    csv_path = os.path.join(DATA_DIR, "drug_features.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}\n"
            "Run: python data/fetch_data.py first"
        )
    df = pd.read_csv(csv_path)
    print(f"📊 Loaded {len(df)} samples")
    print(f"   Features: {FEATURE_COLS}")
    print(f"   Classes: {df['risk_label'].value_counts().to_dict()}")
    return df

def preprocess(df):
    """Extract features and encode labels."""
    X = df[FEATURE_COLS].copy()
    y_raw = df["risk_label"].copy()

    # Encode labels
    le = LabelEncoder()
    le.classes_ = np.array(RISK_LABELS)  # Force order: Low=0, Medium=1, High=2
    y = le.transform(y_raw)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, le, scaler, X.values

def train_model(X, y):
    """Train Neural Network classifier with cross-validation."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation='relu',
        solver='adam',
        alpha=0.001,
        learning_rate='adaptive',
        max_iter=500,
        random_state=42
    )

    print("\n🏋️  Training Neural Network model...")
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n📈 Test Accuracy: {acc*100:.1f}%")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=RISK_LABELS))

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
    print(f"✅ 5-Fold CV Accuracy: {cv_scores.mean()*100:.1f}% ± {cv_scores.std()*100:.1f}%")

    return model

def save_artifacts(model, scaler, le):
    """Save all model artifacts."""
    # Save model
    model_path = os.path.join(ARTIFACTS_DIR, "model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"\n💾 Model saved → {model_path}")

    # Save scaler
    scaler_path = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    print(f"💾 Scaler saved → {scaler_path}")

    # Save label encoder
    le_path = os.path.join(ARTIFACTS_DIR, "label_encoder.pkl")
    with open(le_path, "wb") as f:
        pickle.dump(le, f)
    print(f"💾 LabelEncoder saved → {le_path}")

    # Remove old SHAP explainer if it exists
    explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.pkl")
    if os.path.exists(explainer_path):
        os.remove(explainer_path)

    # Save metadata
    metadata = {
        "feature_cols": FEATURE_COLS,
        "risk_labels": RISK_LABELS,
        "model_type": type(model).__name__,
        "shap_available": False
    }
    meta_path = os.path.join(ARTIFACTS_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved → {meta_path}")

def main():
    print("🚀 AI Side Effect Checker — Model Training (Neural Network)")
    print("=" * 50)

    df = load_data()
    X, y, le, scaler, X_raw = preprocess(df)
    model = train_model(X, y)
    save_artifacts(model, scaler, le)
    print("\n🎉 Training complete! All artifacts saved to model/artifacts/")

if __name__ == "__main__":
    main()
