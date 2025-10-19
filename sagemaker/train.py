#!/usr/bin/env python3
"""
SageMaker Training Script for Mental Health Risk Prediction
Trains ensemble of Random Forest and Gradient Boosting models
"""

import argparse
import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_data(train_path, val_path):
    """Load training and validation data from CSV"""
    logger.info(f"Loading training data from {train_path}")
    train_df = pd.read_csv(os.path.join(train_path, 'train.csv'))
    
    logger.info(f"Loading validation data from {val_path}")
    val_df = pd.read_csv(os.path.join(val_path, 'validation.csv'))
    
    logger.info(f"Training samples: {len(train_df)}")
    logger.info(f"Validation samples: {len(val_df)}")
    
    return train_df, val_df


def prepare_features(df):
    """Prepare features and labels"""
    # Remove non-feature columns
    exclude_cols = ['label', 'sample_id', 'userId']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['label']
    
    # Handle missing values
    X = X.fillna(X.median())
    
    logger.info(f"Features: {len(feature_cols)}")
    logger.info(f"Feature names: {feature_cols[:10]}...")  # Show first 10
    logger.info(f"Class distribution: {y.value_counts().to_dict()}")
    
    return X, y, feature_cols


def train_random_forest(X_train, y_train, args):
    """Train Random Forest classifier"""
    logger.info("Training Random Forest model...")
    
    rf_model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        class_weight=args.class_weight,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    rf_model.fit(X_train, y_train)
    
    logger.info("Random Forest training complete")
    return rf_model


def train_gradient_boosting(X_train, y_train, args):
    """Train Gradient Boosting classifier"""
    logger.info("Training Gradient Boosting model...")
    
    gb_model = GradientBoostingClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=0.1,
        random_state=42,
        verbose=1
    )
    
    gb_model.fit(X_train, y_train)
    
    logger.info("Gradient Boosting training complete")
    return gb_model


def evaluate_model(model, X, y, model_name):
    """Evaluate model performance"""
    logger.info(f"Evaluating {model_name}...")
    
    # Predictions
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]
    
    # Metrics
    auc = roc_auc_score(y, y_prob)
    precision = precision_score(y, y_pred)
    recall = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        'auc': float(auc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'true_positives': int(tp),
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'accuracy': float((tp + tn) / (tp + tn + fp + fn))
    }
    
    logger.info(f"{model_name} Metrics:")
    logger.info(f"  AUC: {auc:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"  Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")
    
    return metrics, y_prob


def evaluate_ensemble(rf_prob, gb_prob, y, threshold=0.5):
    """Evaluate ensemble predictions"""
    logger.info("Evaluating ensemble model...")
    
    # Average probabilities
    ensemble_prob = (rf_prob + gb_prob) / 2
    ensemble_pred = (ensemble_prob >= threshold).astype(int)
    
    # Metrics
    auc = roc_auc_score(y, ensemble_prob)
    precision = precision_score(y, ensemble_pred)
    recall = recall_score(y, ensemble_pred)
    f1 = f1_score(y, ensemble_pred)
    
    # Confusion matrix
    cm = confusion_matrix(y, ensemble_pred)
    tn, fp, fn, tp = cm.ravel()
    
    metrics = {
        'auc': float(auc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'true_positives': int(tp),
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'accuracy': float((tp + tn) / (tp + tn + fp + fn)),
        'threshold': float(threshold)
    }
    
    logger.info("Ensemble Metrics:")
    logger.info(f"  AUC: {auc:.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    
    return metrics


def get_feature_importance(rf_model, gb_model, feature_names):
    """Get feature importance from both models"""
    logger.info("Calculating feature importance...")
    
    # Average importance from both models
    rf_importance = rf_model.feature_importances_
    gb_importance = gb_model.feature_importances_
    avg_importance = (rf_importance + gb_importance) / 2
    
    # Create DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'rf_importance': rf_importance,
        'gb_importance': gb_importance,
        'avg_importance': avg_importance
    }).sort_values('avg_importance', ascending=False)
    
    logger.info("Top 10 most important features:")
    for idx, row in importance_df.head(10).iterrows():
        logger.info(f"  {row['feature']}: {row['avg_importance']:.4f}")
    
    return importance_df


def save_models(rf_model, gb_model, feature_importance, metrics, model_dir):
    """Save trained models and artifacts"""
    logger.info(f"Saving models to {model_dir}")
    
    # Save models
    joblib.dump(rf_model, os.path.join(model_dir, 'rf_model.pkl'))
    joblib.dump(gb_model, os.path.join(model_dir, 'gb_model.pkl'))
    
    # Save feature importance
    feature_importance.to_csv(os.path.join(model_dir, 'feature_importance.csv'), index=False)
    
    # Save metrics
    with open(os.path.join(model_dir, 'metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info("Models and artifacts saved successfully")


def main():
    """Main training function"""
    parser = argparse.ArgumentParser()
    
    # Hyperparameters
    parser.add_argument('--n_estimators', type=int, default=200)
    parser.add_argument('--max_depth', type=int, default=10)
    parser.add_argument('--min_samples_split', type=int, default=5)
    parser.add_argument('--class_weight', type=str, default='balanced')
    
    # SageMaker specific arguments
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--validation', type=str, default=os.environ.get('SM_CHANNEL_VALIDATION'))
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    
    args = parser.parse_args()
    
    logger.info("="*60)
    logger.info("Mental Health Risk Prediction Model Training")
    logger.info("="*60)
    logger.info(f"Hyperparameters:")
    logger.info(f"  n_estimators: {args.n_estimators}")
    logger.info(f"  max_depth: {args.max_depth}")
    logger.info(f"  min_samples_split: {args.min_samples_split}")
    logger.info(f"  class_weight: {args.class_weight}")
    logger.info("="*60)
    
    # Load data
    train_df, val_df = load_data(args.train, args.validation)
    
    # Prepare features
    X_train, y_train, feature_names = prepare_features(train_df)
    X_val, y_val, _ = prepare_features(val_df)
    
    # Train models
    rf_model = train_random_forest(X_train, y_train, args)
    gb_model = train_gradient_boosting(X_train, y_train, args)
    
    # Evaluate on validation set
    rf_metrics, rf_prob = evaluate_model(rf_model, X_val, y_val, "Random Forest")
    gb_metrics, gb_prob = evaluate_model(gb_model, X_val, y_val, "Gradient Boosting")
    ensemble_metrics = evaluate_ensemble(rf_prob, gb_prob, y_val)
    
    # Feature importance
    feature_importance = get_feature_importance(rf_model, gb_model, feature_names)
    
    # Combine metrics
    all_metrics = {
        'random_forest': rf_metrics,
        'gradient_boosting': gb_metrics,
        'ensemble': ensemble_metrics,
        'training_samples': len(train_df),
        'validation_samples': len(val_df),
        'num_features': len(feature_names)
    }
    
    # Save models
    save_models(rf_model, gb_model, feature_importance, all_metrics, args.model_dir)
    
    logger.info("="*60)
    logger.info("Training Complete!")
    logger.info(f"Final Ensemble AUC: {ensemble_metrics['auc']:.4f}")
    logger.info(f"Final Ensemble Recall: {ensemble_metrics['recall']:.4f}")
    logger.info("="*60)


if __name__ == '__main__':
    main()
