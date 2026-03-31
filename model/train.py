"""
Train XGBoost model on drug feature dataset + generate SHAP explanations.
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
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import xgboost as xgb
    print("✅ XGBoost available")
except ImportError:
    print("⚠️  XGBoost not found, using RandomForest fallback")
    from sklearn.ensemble import RandomForestClassifier

try:
    import shap
    print("✅ SHAP available")
    SHAP_AVAILABLE = True
except ImportError:
    print("⚠️  SHAP not found — explanations will be feature-importance based")
    SHAP_AVAILABLE = False

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
    """Train XGBoost classifier with cross-validation."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    try:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1
        )
    except (NameError, Exception):
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

    print("\n🏋️  Training model...")
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

    return model, X_train, X_test, y_train, y_test


def compute_shap_values(model, X_train, X_test):
    """Compute SHAP values for explainability (XGBoost multi-class safe)."""
    if not SHAP_AVAILABLE:
        return None

    print("\n🔍 Computing SHAP values...")
    try:
        # Use the newer Explainer API which handles multi-class correctly
        explainer = shap.Explainer(model, X_train)
        shap_values = explainer(X_test)

        # shap_values.values shape: (n_samples, n_features, n_classes) for multi-class
        vals = shap_values.values
        if vals.ndim == 3:
            # Average absolute SHAP across all classes
            mean_abs_shap = np.mean(np.abs(vals), axis=(0, 2))
        elif vals.ndim == 2:
            mean_abs_shap = np.abs(vals).mean(axis=0)
        else:
            mean_abs_shap = np.abs(vals)

        feature_importance_dict = {
            feat: float(imp)
            for feat, imp in zip(FEATURE_COLS, mean_abs_shap)
        }

        print("Feature Importance (SHAP):")
        for feat, imp in sorted(feature_importance_dict.items(), key=lambda x: -x[1]):
            bar = "#" * int(imp * 20)
            print(f"   {feat:30s}: {imp:.4f}  {bar}")

        return explainer, shap_values
    except Exception as e:
        print(f"SHAP Explainer failed (new API): {e}")
        # Fallback to TreeExplainer
        try:
            explainer = shap.TreeExplainer(model)
            shap_values_raw = explainer.shap_values(X_test)

            if isinstance(shap_values_raw, list):
                # list of (n_samples, n_features) arrays — one per class
                stacked = np.stack([np.abs(sv) for sv in shap_values_raw], axis=2)
                mean_abs_shap = stacked.mean(axis=(0, 2))
            elif shap_values_raw.ndim == 3:
                mean_abs_shap = np.abs(shap_values_raw).mean(axis=(0, 2))
            else:
                mean_abs_shap = np.abs(shap_values_raw).mean(axis=0)

            print("Feature Importance (TreeExplainer fallback):")
            for feat, imp in zip(FEATURE_COLS, mean_abs_shap):
                print(f"   {feat}: {float(imp):.4f}")

            return explainer, shap_values_raw
        except Exception as e2:
            print(f"TreeExplainer also failed: {e2}")
            return None


def save_artifacts(model, scaler, le, explainer=None):
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

    # Save SHAP explainer
    if explainer is not None:
        explainer_path = os.path.join(ARTIFACTS_DIR, "shap_explainer.pkl")
        with open(explainer_path, "wb") as f:
            pickle.dump(explainer, f)
        print(f"💾 SHAP explainer saved → {explainer_path}")

    # Save metadata
    metadata = {
        "feature_cols": FEATURE_COLS,
        "risk_labels": RISK_LABELS,
        "model_type": type(model).__name__,
        "shap_available": SHAP_AVAILABLE and explainer is not None
    }
    meta_path = os.path.join(ARTIFACTS_DIR, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved → {meta_path}")


def main():
    print("🚀 AI Side Effect Checker — Model Training")
    print("=" * 50)

    df = load_data()
    X, y, le, scaler, X_raw = preprocess(df)
    model, X_train, X_test, y_train, y_test = train_model(X, y)

    shap_result = compute_shap_values(model, X_train, X_test)
    explainer = None
    if shap_result is not None:
        explainer = shap_result[0]

    save_artifacts(model, scaler, le, explainer)

    print("\n🎉 Training complete! All artifacts saved to model/artifacts/")


if __name__ == "__main__":
    main()
